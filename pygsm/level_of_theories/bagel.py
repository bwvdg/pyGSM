# standard library imports
import sys
import subprocess
import json
from os import path
from copy import deepcopy

# third party
import numpy as np

# local application imports
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
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
        self.bagel_archive = path.join(self.scratch_dir, options['bagel_archive'])
        self.bagel_inpath = path.join(self.scratch_dir, options['bagel_inpath'])
        self.bagel_gradpath = path.join(self.scratch_dir, options['bagel_gradpath'])
        self.bagel_outpath = path.join(self.scratch_dir, options['bagel_outpath'])

    # given geom, mult, state, write input file

    @classmethod
    def default_options(cls, **kwargs):
        bagel_opts = super(BAGEL, cls).default_options()
        bagel_opts.add_option(key="bagel_runpath", required=True, value="", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_archive", required=False, value="bagel.archive", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_inpath", required=False, value="bagel.json", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_gradpath", required=False, value="force.json", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_outpath", required=False, value="bagel.out", allowed_types=[str], doc='')
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
      if path.exists(path.join(self.bagel_archive)):
          cur_bagel_data['bagel'].insert(0, load_ref)
      # write the input file
      print(f"writing to bagel path: {self.bagel_inpath}")
      with open(self.bagel_inpath, 'w') as bagel_infile:
          json.dump(cur_bagel_data, bagel_infile, indent=2)

    def read_output(self):
        with open(self.bagel_gradpath, 'r') as bagel_gradfile:
            bagel_outdata = json.load(bagel_gradfile)
            self.energy = bagel_outdata['energy']
            self.gradient = np.asarray([atom['xyz'] for atom in bagel_outdata['gradient']])

    def run(self, geom, multiplicity, state, verbose=False):
        
        print("writing bagel input")
        self.write_input(geom)

        # get energies
        print("running bagel")
        process = subprocess.Popen(self.bagel_runpath, cwd=self.scratch_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bagelout, bagelerr = process.communicate()
        #print(f"bagelout: \n{bagelout}")
        #print(f"bagelerr: \n{bagelerr}")
        self.read_output()

        # energy in hartree
        self._Energies[(multiplicity, state)] = self.Energy(self.energy, 'Hartree')

        # grad 
        gradunit = "Hartree/Angstrom" if self.angstrom else "Hartree/Bohr"
        self._Gradients[(multiplicity, state)] = self.Gradient(self.gradient, gradunit)

        # write E to scratch
        self.write_E_to_file()

        #res = None

        #return res


if __name__ == "__main__":
    pass

#    geom = manage_xyz.read_xyz('../../data/ethylene.xyz')
#    # geoms=manage_xyz.read_xyzs('../../data/diels_alder.xyz')
#    # geom = geoms[0]
#    # geom=manage_xyz.read_xyz('xtbopt.xyz')
#    xyz = manage_xyz.xyz_to_np(geom)
#    # xyz *= units.ANGSTROM_TO_AU
#
#    lot = bagel_lot.from_options(states=[(1, 0)], gradient_states=[(1, 0)], geom=geom, node_id=0)
#
#    E = lot.get_energy(xyz, 1, 0)
#    print(E)
#
#    g = lot.get_gradient(xyz, 1, 0)
#    print(g)
