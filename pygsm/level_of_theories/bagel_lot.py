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


class bagel_lot(Lot):
    def __init__(self, options):
        super(bagel_lot, self).__init__(options)
        # get the input file
        with open(self.lot_input_file, 'r') as bagel_infile:
          self.bagel_data = json.load(bagel_infile)
        # get the save reference 
        self.bagel_runpath = options.bagel_runpath
        self.bagel_refpath = os.path.join(self.scratch_dir, 'bagel.archive')
        self.bagel_inpath = os.path.join(self.scratch_dir, 'bagel.json')
        self.bagel_outpath = os.path.join(self.scratch_dir, 'force.json')


    # given geom, mult, state, write input file

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
      if os.path.exists(os.path.join(self.bagel_ref_path)):
          cur_bagel_data['bagel'].insert(0, load_ref)

      # update the geometry
      self.set_geom(geom)

      # write the input file
      with open(bagel_input_path, 'w') as bagel_input_file
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
