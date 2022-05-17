# standard library imports
import sys
import subprocess
import json
import os
import time

from io import StringIO

from copy import deepcopy

# third party
import numpy as np

# local application imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities import manage_xyz, units, elements
try:
    from .base_lot import Lot
except:
    from base_lot import Lot


class BAGEL(Lot):
    def __init__(self, options):
        super(BAGEL, self).__init__(options)
        # get the input file
        with open(self.lot_inp_file, 'r') as bagel_infile:
            self.bagel_data = json.load(bagel_infile)
        # get file locations
        self.bagel_runpath = options['bagel_runpath']
        self.bagel_archivepath = os.path.join(self.scratch_dir, options['bagel_archive'] + ".archive.0")
        self.bagel_archive = options['bagel_archive']
        self.bagel_inpath = os.path.join(self.scratch_dir, options['bagel_inpath'])
        self.bagel_gradpath = os.path.join(self.scratch_dir, options['bagel_gradpath'])
        self.bagel_outpath = os.path.join(self.scratch_dir, options['bagel_outpath'])
        self.bagel_errpath = os.path.join(self.scratch_dir, options['bagel_errpath'])
        # find the archive path of a neighboring node
        adjacent_node_id = self.node_id - 1 if self.node_id > 0 else 1 
        adjacent_scratch_dir = self.get_scratch_dir(self.ID, adjacent_node_id)
        self.adjacent_bagel_archivepath = os.path.join(adjacent_scratch_dir, self.bagel_archive)
        # set an initial run index to label bagel output
        self.run_index = 0

    # given geom, mult, state, write input file

    @classmethod
    def default_options(cls, **kwargs):
        bagel_opts = super(BAGEL, cls).default_options()
        bagel_opts.add_option(key="bagel_runpath", required=True, value="", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_archive", required=False, value="bagel", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_inpath", required=False, value="bagel.json", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_gradpath", required=False, value="force.json", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_outpath", required=False, value="bagel.out", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_errpath", required=False, value="bagel.err", allowed_types=[str], doc='')
        return bagel_opts.copy()

    def set_geom(self, geom, bagel_data):
        for bagel_block in bagel_data['bagel']:
            if 'geometry' in bagel_block:
                bagel_block['geometry'] = [{'atom': asym, 'xyz': [x, y, z]} for (asym, x, y, z) in geom]
                self.angstrom = bagel_block['angstrom']


    def write_input(self, geom):
        cur_bagel_data = deepcopy(self.bagel_data)
        # update the geometry
        self.set_geom(geom, cur_bagel_data)
        # check if bagel archive exists, and add the archive block if so
        load_ref = {'title': "load_ref", 'file': self.bagel_archive, 'nocompute': True}
        if os.path.exists(self.bagel_archivepath):
            cur_bagel_data['bagel'].insert(0, load_ref)
        # check if the bagel archive from the adjacent node; copy over and add the blcok if soif so
        elif os.path.exists(self.adjacent_bagel_archivepath):
            shutil.copy2(self.adjacent_bagel_archivepath, self.bagel_archivepath)
            cur_bagel_data['bagel'].insert(0, load_ref)
        # write the input file
        with open(self.bagel_inpath, 'w') as bagel_infile:
            json.dump(cur_bagel_data, bagel_infile, indent=2)

    def read_grad(self):
        with open(self.bagel_gradpath, 'r') as bagel_gradfile:
            bagel_outdata = json.load(bagel_gradfile)
            self.energy = bagel_outdata['energy']
            self.gradient = np.asarray([atom['xyz'] for atom in bagel_outdata['gradient']])

    def run(self, geom, multiplicity, state, verbose=False):
        
        print(f"Running BAGEL on node {self.node_id}.")
        self.write_input(geom)
        gradunit = "Hartree/Angstrom" if self.angstrom else "Hartree/Bohr"
        
        # run bagel
        time_start = time.time()
        bagel_outpath = self.bagel_outpath + f".{self.run_index:03d}"
        bagel_errpath = self.bagel_outpath + f".{self.run_index:03d}"
        with open(bagel_outpath, 'w') as bagel_outfile, open(bagel_errpath, 'w') as bagel_errfile:
            process = subprocess.Popen(self.bagel_runpath, cwd=self.scratch_dir, shell=True, stdout=bagel_outfile, stderr=bagel_errfile)
        process.communicate()
        bagel_time = time.time() - time_start

        # check if successful, read output, and report summary
        rcode = process.returncode
        if rcode != 0:
            raise Exception(f"Bagel error, rcode {rcode}: \n{errstring}")
        self.read_grad()
        print(f"Finished BAGEL on node {self.node_id}. Runtime: {bagel_time}, energy: {self.energy}, gradmag: {np.linalg.norm(self.gradient)}")

        # collect energy and gradients
        self._Energies[(multiplicity, state)] = self.Energy(self.energy, 'Hartree')
        self._Gradients[(multiplicity, state)] = self.Gradient(self.gradient, gradunit)
        # write E to scratch
        self.run_index += 1
        self.write_E_to_file()


if __name__ == "__main__":
    pass
