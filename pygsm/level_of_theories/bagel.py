# standard library imports
import sys
from os import path

# third party
import numpy as np
import json
from copy import deepcopy

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
        self.bagel_archive = options['bagel_archive']
        self.bagel_inpath = options['bagel_inpath']
        self.bagel_outpath = options['bagel_outpath']

    # given geom, mult, state, write input file

    @classmethod
    def default_options(cls, **kwargs):
        bagel_opts = super(BAGEL, cls).default_options()
        bagel_opts.add_option(key="bagel_runpath", required=True, value="", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_archive", required=False, value="bagel.archive", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_inpath", required=False, value="bagel.json", allowed_types=[str], doc='')
        bagel_opts.add_option(key="bagel_outpath", required=False, value="force.json", allowed_types=[str], doc='')
        return bagel_opts.copy()

    def set_geom(self, geom):
        for g in geom:
            print(g)
        pass

    def write_input(self, geom):
      self.bagel_template_path = ""
      self.bagel_ref_path = ""

      cur_bagel_data = deepcopy(self.bagel_data)

      # check if bagel archive exists, and add the archive block if so
      load_ref = {'title': "load_ref", 'file': self.bagel_ref_path, 'nocompute': True}
      if path.exists(path.join(self.bagel_ref_path)):
          cur_bagel_data['bagel'].insert(0, load_ref)

      # update the geometry
      self.set_geom(geom)

      # write the input file
      with open(bagel_input_path, 'w') as bagel_input_file:
          json.dump(cur_bagel_data, bagel_input_file)

    def run(self, geom, multiplicity, state, verbose=False):
        
        print("running bagel")
        print(f"  bagel infile  {self.bagel_inpath}")
        print(f"  bagel outfile {self.bagel_outpath}")
        print(f"  bagel runpath {self.bagel_runpath}")
        print(f"  bagel refpath {self.bagel_refpath}")

        # energy in hartree
        #self._Energies[(multiplicity, state)] = self.Energy(res.get_energy(), 'Hartree')

        # grad in Hatree/Bohr
        #self._Gradients[(multiplicity, state)] = self.Gradient(res.get_gradient(), 'Hartree/Bohr')

        # write E to scratch
        #self.write_E_to_file()

        res = None

        return res


#if __name__ == "__main__":
#
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
