from __future__ import print_function
import os
import unittest
from numpy import unique
from six import iteritems

import pyNastran
test_path = pyNastran.__path__[0]

from pyNastran.bdf.bdf import BDF
from pyNastran.op2.op2 import OP2, FatalError
from pyNastran.op2.test.test_op2 import run_op2
from pyNastran.bdf.test.bdf_unit_tests import Tester
from pyNastran.op2.tables.oef_forces.oef_forceObjects import RealPlateBilinearForceArray, RealPlateForceArray

class TestOP2(Tester):
    #def _spike(self):
        #op2 = OP2()
        #op2.set_results('solidStress.oxx')
        #op2.read_op2(op2_filename, vectorized=False)

    def test_set_results(self):
        folder = os.path.abspath(os.path.join(test_path, '..', 'models'))
        op2_filename = os.path.join(folder, 'solid_bending', 'solid_bending.op2')

        op2 = OP2(debug=False)
        op2.set_results('stress')
        op2.read_op2(op2_filename)
        self.assertEqual(len(op2.cpenta_stress), 0, len(op2.cpenta_stress))
        self.assertEqual(len(op2.chexa_stress), 0, len(op2.chexa_stress))
        self.assertEqual(len(op2.ctetra_stress), 1, len(op2.ctetra_stress))
        self.assertEqual(len(op2.displacements), 0, len(op2.displacements))

        op2 = OP2(debug=False)
        op2.set_results(['stress', 'displacements'])
        op2.read_op2(op2_filename)
        self.assertEqual(len(op2.cpenta_stress), 0, len(op2.cpenta_stress))
        self.assertEqual(len(op2.chexa_stress), 0, len(op2.chexa_stress))
        self.assertEqual(len(op2.ctetra_stress), 1, len(op2.ctetra_stress))
        self.assertEqual(len(op2.displacements), 1, len(op2.displacements))

    def test_op2_solid_bending_01(self):
        op2_filename = os.path.join('solid_bending.op2')
        folder = os.path.abspath(os.path.join(test_path, '..', 'models', 'solid_bending'))
        op2_filename = os.path.join(folder, op2_filename)
        make_geom = False
        write_bdf = False
        write_f06 = True
        debug = False
        #debug_file = 'solid_bending.debug.out'
        model, ext = os.path.splitext(op2_filename)
        debug_file = model + '.debug.out'

        if os.path.exists(debug_file):
            os.remove(debug_file)
        run_op2(op2_filename, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                write_f06=write_f06,
                debug=debug, stop_on_failure=True, binary_debug=True, quiet=True)
        assert os.path.exists(debug_file), os.listdir(folder)
        #os.remove(debug_file)

        make_geom = False
        write_bdf = False
        write_f06 = True
        run_op2(op2_filename, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                write_f06=write_f06,
                debug=debug, stop_on_failure=True, binary_debug=True, quiet=True)
        assert os.path.exists(debug_file), os.listdir(folder)
        os.remove(debug_file)

    def test_op2_solid_shell_bar_01(self):
        op2_filename = os.path.join('static_solid_shell_bar.op2')
        folder = os.path.abspath(os.path.join(test_path, '..', 'models', 'sol_101_elements'))
        op2_filename = os.path.join(folder, op2_filename)
        make_geom = False
        write_bdf = False
        write_f06 = True
        debug = False
        #debug_file = 'solid_bending.debug.out'
        model, ext = os.path.splitext(op2_filename)
        debug_file = model + '.debug.out'

        if os.path.exists(debug_file):
            os.remove(debug_file)
        op2, is_passed = run_op2(op2_filename, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                                 write_f06=write_f06,
                                 debug=debug, stop_on_failure=True, binary_debug=True, quiet=True)

        isubcase = 1
        rod_force = op2.crod_force[isubcase]
        assert rod_force.nelements == 2, rod_force.nelements
        assert rod_force.data.shape == (1, 2, 2), rod_force.data.shape

        rod_stress = op2.crod_stress[isubcase]
        assert rod_stress.nelements == 2, rod_stress.nelements
        assert rod_stress.data.shape == (1, 2, 4), rod_stress.data.shape

        cbar_stress = op2.cbar_stress[isubcase]
        assert cbar_stress.nelements == 1, cbar_stress.nelements
        assert cbar_stress.data.shape == (1, 1, 15), cbar_stress.data.shape

        cbeam_stress = op2.cbeam_stress[isubcase]
        assert cbeam_stress.nelements == 11, cbeam_stress.nelements  # wrong
        assert cbeam_stress.data.shape == (1, 11, 8), cbeam_stress.data.shape

        cquad4_stress = op2.cquad4_stress[isubcase]
        assert cquad4_stress.nelements == 20, cquad4_stress.nelements
        assert cquad4_stress.data.shape == (1, 20, 8), cquad4_stress.data.shape

        ctria3_stress = op2.ctria3_stress[isubcase]
        assert ctria3_stress.nelements == 8, ctria3_stress.nelements
        assert ctria3_stress.data.shape == (1, 8, 8), ctria3_stress.data.shape

        ctetra_stress = op2.ctetra_stress[isubcase]
        assert ctetra_stress.nelements == 2, ctetra_stress.nelements
        assert ctetra_stress.data.shape == (1, 10, 10), ctetra_stress.data.shape

        cpenta_stress = op2.cpenta_stress[isubcase]
        assert cpenta_stress.nelements == 2, cpenta_stress.nelements
        assert cpenta_stress.data.shape == (1, 14, 10), cpenta_stress.data.shape

        chexa_stress = op2.chexa_stress[isubcase]
        assert chexa_stress.nelements == 1, chexa_stress.nelements
        assert chexa_stress.data.shape == (1, 9, 10), chexa_stress.data.shape

        assert os.path.exists(debug_file), os.listdir(folder)
        os.remove(debug_file)

    def test_op2_solid_shell_bar_02(self):
        op2_filename = os.path.join('mode_solid_shell_bar.op2')
        folder = os.path.abspath(os.path.join(test_path, '..', 'models', 'sol_101_elements'))
        op2_filename = os.path.join(folder, op2_filename)
        make_geom = False
        write_bdf = False
        write_f06 = True
        debug = False
        #debug_file = 'solid_bending.debug.out'
        model, ext = os.path.splitext(op2_filename)
        debug_file = model + '.debug.out'

        if os.path.exists(debug_file):
            os.remove(debug_file)
        op2, is_passed = run_op2(op2_filename, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                                 write_f06=write_f06,
                                 debug=debug, stop_on_failure=True, binary_debug=True, quiet=True)

        isubcase = 1
        rod_force = op2.crod_force[isubcase]
        assert rod_force.nelements == 2, rod_force.nelements
        assert rod_force.data.shape == (3, 2, 2), rod_force.data.shape

        rod_stress = op2.crod_stress[isubcase]
        assert rod_stress.nelements == 2, rod_stress.nelements
        assert rod_stress.data.shape == (3, 2, 4), rod_stress.data.shape

        cbar_stress = op2.cbar_stress[isubcase]
        assert cbar_stress.nelements == 3, cbar_stress.nelements  # TODO: wrong
        assert cbar_stress.data.shape == (3, 1, 15), cbar_stress.data.shape

        cbeam_stress = op2.cbeam_stress[isubcase]
        assert cbeam_stress.nelements == 11, cbeam_stress.nelements  # TODO: wrong
        assert cbeam_stress.data.shape == (3, 11, 8), cbeam_stress.data.shape

        cquad4_stress = op2.cquad4_stress[isubcase]
        assert cquad4_stress.nelements == 60, cquad4_stress.nelements # TODO: wrong
        assert cquad4_stress.data.shape == (3, 20, 8), cquad4_stress.data.shape

        ctria3_stress = op2.ctria3_stress[isubcase]
        assert ctria3_stress.nelements == 24, ctria3_stress.nelements # TODO: wrong
        assert ctria3_stress.data.shape == (3, 8, 8), ctria3_stress.data.shape

        ctetra_stress = op2.ctetra_stress[isubcase]
        assert ctetra_stress.nelements == 2, ctetra_stress.nelements
        assert ctetra_stress.data.shape == (3, 10, 10), ctetra_stress.data.shape

        cpenta_stress = op2.cpenta_stress[isubcase]
        assert cpenta_stress.nelements == 2, cpenta_stress.nelements
        assert cpenta_stress.data.shape == (3, 14, 10), cpenta_stress.data.shape

        chexa_stress = op2.chexa_stress[isubcase]
        assert chexa_stress.nelements == 1, chexa_stress.nelements
        assert chexa_stress.data.shape == (3, 9, 10), chexa_stress.data.shape

        assert os.path.exists(debug_file), os.listdir(folder)
        os.remove(debug_file)

    def test_op2_solid_shell_bar_03(self):
        op2_filename = os.path.join('buckling_solid_shell_bar.op2')
        folder = os.path.abspath(os.path.join(test_path, '..', 'models', 'sol_101_elements'))
        op2_filename = os.path.join(folder, op2_filename)
        make_geom = False
        write_bdf = False
        write_f06 = True
        debug = False
        #debug_file = 'solid_bending.debug.out'
        model, ext = os.path.splitext(op2_filename)
        debug_file = model + '.debug.out'

        if os.path.exists(debug_file):
            os.remove(debug_file)
        op2, is_passed = run_op2(op2_filename, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                                 write_f06=write_f06,
                                 debug=debug, stop_on_failure=True, binary_debug=True, quiet=True)

        isubcases = [(1, 1, 1, 0, 'DEFAULT1'), (1, 8, 1, 0, 'DEFAULT1')]
        isubcase = isubcases[1]

        try:
            rod_force = op2.crod_force[isubcase]
        except KeyError:
            msg = 'isubcase=%s was not found\nkeys=%s' % (isubcase, op2.crod_force.keys())
            raise KeyError(msg)
        assert rod_force.nelements == 2, rod_force.nelements
        assert rod_force.data.shape == (4, 2, 2), rod_force.data.shape

        rod_stress = op2.crod_stress[isubcase]
        assert rod_stress.nelements == 2, rod_stress.nelements
        assert rod_stress.data.shape == (4, 2, 4), rod_stress.data.shape

        cbar_stress = op2.cbar_stress[isubcase]
        assert cbar_stress.nelements == 4, cbar_stress.nelements  # TODO: wrong
        assert cbar_stress.data.shape == (4, 1, 15), cbar_stress.data.shape

        cbeam_stress = op2.cbeam_stress[isubcase]
        assert cbeam_stress.nelements == 11, cbeam_stress.nelements  # TODO: wrong
        assert cbeam_stress.data.shape == (4, 11, 8), cbeam_stress.data.shape

        cquad4_stress = op2.cquad4_stress[isubcase]
        assert cquad4_stress.nelements == 80, cquad4_stress.nelements # TODO: wrong
        assert cquad4_stress.data.shape == (4, 20, 8), cquad4_stress.data.shape

        ctria3_stress = op2.ctria3_stress[isubcase]
        assert ctria3_stress.nelements == 32, ctria3_stress.nelements # TODO: wrong
        assert ctria3_stress.data.shape == (4, 8, 8), ctria3_stress.data.shape

        ctetra_stress = op2.ctetra_stress[isubcase]
        assert ctetra_stress.nelements == 2, ctetra_stress.nelements
        assert ctetra_stress.data.shape == (4, 10, 10), ctetra_stress.data.shape

        cpenta_stress = op2.cpenta_stress[isubcase]
        assert cpenta_stress.nelements == 2, cpenta_stress.nelements
        assert cpenta_stress.data.shape == (4, 14, 10), cpenta_stress.data.shape

        chexa_stress = op2.chexa_stress[isubcase]
        assert chexa_stress.nelements == 1, chexa_stress.nelements
        assert chexa_stress.data.shape == (4, 9, 10), chexa_stress.data.shape

        assert os.path.exists(debug_file), os.listdir(folder)
        os.remove(debug_file)

    def test_op2_solid_shell_bar_04(self):
        op2_filename = os.path.join('freq_solid_shell_bar.op2')
        folder = os.path.abspath(os.path.join(test_path, '..', 'models', 'sol_101_elements'))
        op2_filename = os.path.join(folder, op2_filename)
        make_geom = False
        write_bdf = False
        write_f06 = True
        debug = False
        #debug_file = 'solid_bending.debug.out'
        model, ext = os.path.splitext(op2_filename)
        debug_file = model + '.debug.out'

        if os.path.exists(debug_file):
            os.remove(debug_file)
        op2, is_passed = run_op2(op2_filename, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                                 write_f06=write_f06,
                                 debug=debug, stop_on_failure=True, binary_debug=True, quiet=True)
        isubcase = 1
        # rod_force = op2.crod_force[isubcase]
        # assert rod_force.nelements == 2, rod_force.nelements
        # assert rod_force.data.shape == (7, 2, 2), rod_force.data.shape


        # isubcases = [(1, 1, 1, 0, 'DEFAULT'), (1, 8, 1, 0, 'DEFAULT')]
        # isubcase = isubcases[1]

        rod_force = op2.crod_force[isubcase]
        assert rod_force.nelements == 2, rod_force.nelements
        assert rod_force.data.shape == (7, 2, 2), rod_force.data.shape

        rod_stress = op2.crod_stress[isubcase]
        assert rod_stress.nelements == 2, rod_stress.nelements
        assert rod_stress.data.shape == (7, 2, 2), rod_stress.data.shape

        cbar_stress = op2.cbar_stress[isubcase]
        assert cbar_stress.nelements == 1, cbar_stress.nelements
        assert cbar_stress.data.shape == (7, 1, 9), cbar_stress.data.shape

        #print(op2.cbeam_stress.keys())
        # cbeam_stress = op2.cbeam_stress[isubcase]
        # assert cbeam_stress.nelements == 11, cbeam_stress.nelements  # TODO: wrong
        # assert cbeam_stress.data.shape == (7, 11, 8), cbeam_stress.data.shape

        cquad4_stress = op2.cquad4_stress[isubcase]
        assert cquad4_stress.nelements == 4, cquad4_stress.nelements # TODO: wrong
        assert cquad4_stress.data.shape == (7, 40, 3), cquad4_stress.data.shape

        #print(op2.ctria3_stress.keys())
        ctria3_stress = op2.ctria3_stress[isubcase]
        assert ctria3_stress.nelements == 8, ctria3_stress.nelements # TODO: wrong
        assert ctria3_stress.data.shape == (7, 32, 3), ctria3_stress.data.shape

        ctetra_stress = op2.ctetra_stress[isubcase]
        assert ctetra_stress.nelements == 2, ctetra_stress.nelements
        assert ctetra_stress.data.shape == (7, 10, 6), ctetra_stress.data.shape

        cpenta_stress = op2.cpenta_stress[isubcase]
        assert cpenta_stress.nelements == 2, cpenta_stress.nelements
        assert cpenta_stress.data.shape == (7, 14, 6), cpenta_stress.data.shape

        chexa_stress = op2.chexa_stress[isubcase]
        assert chexa_stress.nelements == 1, chexa_stress.nelements
        assert chexa_stress.data.shape == (7, 9, 6), chexa_stress.data.shape

        assert os.path.exists(debug_file), os.listdir(folder)
        os.remove(debug_file)

    def test_op2_plate_py_01(self):
        op2_filename = os.path.join('plate_py', 'plate_py.op2')
        folder = os.path.abspath(os.path.join(test_path, '..', 'models'))
        make_geom = False
        write_bdf = False
        write_f06 = False
        debug = False
        op2file = os.path.join(folder, op2_filename)
        run_op2(op2file, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                write_f06=write_f06,
                debug=debug, stop_on_failure=True, quiet=True)

        make_geom = False
        write_bdf = False
        write_f06 = True
        run_op2(op2file, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                write_f06=write_f06,
                debug=debug, stop_on_failure=True, quiet=True)

    def test_op2_good_sine_01(self):
        op2_filename = os.path.join('freq_sine', 'good_sine.op2')
        folder = os.path.abspath(os.path.join(test_path, '..', 'models'))
        make_geom = False
        write_bdf = False
        write_f06 = False
        debug = False
        op2file = os.path.join(folder, op2_filename)
        op2i, is_passed = run_op2(op2file, make_geom=make_geom, write_bdf=write_bdf, isubcases=[],
                                  write_f06=write_f06,
                                  debug=debug, stop_on_failure=True,
                                  quiet=True)

        nids = [5]
        isubcase = 103
        with self.assertRaises(AssertionError):
            # no index 0; fortran 1-based
            try:
                acc = op2i.accelerations[isubcase]
            except KeyError:
                raise KeyError('getting accelerations; isubcase=%s; keys=%s' % (
                    isubcase, op2i.accelerations.keys()))

            acc.extract_xyplot(nids, 0, 'real')

        accx = op2i.accelerations[103].extract_xyplot(nids, 1, 'real')
        accxi = op2i.accelerations[103].extract_xyplot(nids, 1, 'imag')
        #print(accx)
        #print(accxi)
        #make_geom = False
        #write_bdf = False
        #write_f06 = True
        #run_op2(op2file, make_geom=make_geom, write_bdf=write_bdf, iSubcases=[],
                #write_f06=write_f06,
                #debug=debug, stopOnFailure=True)

    def test_op2_good_sine_02(self):
        folder = os.path.abspath(os.path.join(test_path, '..', 'models'))
        bdf_filename = os.path.join(folder, 'freq_sine', 'good_sine.dat')
        op2_filename = os.path.join(folder, 'freq_sine', 'good_sine.op2')
        make_geom = False
        write_bdf = False
        write_f06 = True
        debug = False
        op2file = os.path.join(folder, op2_filename)
        bdf = BDF(debug=False)
        bdf.read_bdf(bdf_filename)

        debug = False
        debug_file = 'debug.out'

        op2 = OP2(debug=debug, debug_file=debug_file)
        op2.read_op2(op2_filename)
        assert os.path.exists(debug_file), os.listdir('.')

        self._verify_ids(bdf, op2, isubcase=1)

    def test_op2_bcell_01(self):
        folder = os.path.abspath(os.path.join(test_path, '..', 'models'))
        bdf_filename = os.path.join(folder, 'other', 'bcell9p0.bdf')
        op2_filename = os.path.join(folder, 'other', 'bcell9p0.op2')
        make_geom = False
        write_bdf = False
        write_f06 = True
        debug = False
        op2file = os.path.join(folder, op2_filename)
        bdf = BDF(debug=False)
        bdf.read_bdf(bdf_filename, xref=False)

        debug = False
        debug_file = 'debug.out'
        op2 = OP2(debug=debug, debug_file=debug_file)
        op2.read_op2(op2_filename)
        assert os.path.exists(debug_file), os.listdir('.')

        self._verify_ids(bdf, op2, isubcase=1)

        msg = ''
        for isubcase, keys in sorted(iteritems(op2.subcase_key)):
            if len(keys) != 1:
                msg += 'isubcase=%s keys=%s len(keys) != 1\n' % (isubcase, keys)
                if len(keys) == 0:
                    continue
            if isubcase != keys[0]:
                msg += 'isubcase=%s != key0=%s keys=%s\n' % (isubcase, keys[0], keys)
        if msg:
            assert msg == '', msg
        op2.write_f06('junk.f06', quiet=True)
        os.remove('junk.f06')


    def _verify_ids(self, bdf, op2, isubcase=1):
        types = ['CQUAD4', 'CTRIA3', 'CHEXA', 'CPENTA', 'CTETRA', 'CROD', 'CONROD', 'CTUBE']
        out = bdf.get_card_ids_by_card_types(types)

        card_type = 'CQUAD4'
        if op2.cquad4_stress:
            try:
                case = op2.cquad4_stress[isubcase]
            except KeyError:
                raise KeyError('getting cquad4_stress; isubcase=%s; keys=%s' % (
                    isubcase, op2.cquad4_stress.keys()))
            eids = unique(case.element_node[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.cquad4_strain:
            try:
                case = op2.cquad4_strain[isubcase]
            except KeyError:
                raise KeyError('getting cquad4_strain; isubcase=%s; keys=%s' % (
                    isubcase, op2.cquad4_strain.keys()))
            eids = unique(case.element_node[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.cquad4_composite_strain:
            try:
                case = op2.cquad4_composite_strain[isubcase]
            except KeyError:
                raise KeyError('getting cquad4_composite_strain; isubcase=%s; keys=%s' % (
                    isubcase, op2.cquad4_composite_strain.keys()))
            eids = unique(case.element_layer[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.cquad4_composite_stress:
            try:
                case = op2.cquad4_composite_stress[isubcase]
            except KeyError:
                raise KeyError('getting cquad4_composite_stress; isubcase=%s; keys=%s' % (
                    isubcase, op2.cquad4_composite_stress.keys()))

            eids = unique(case.element_layer[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.cquad4_force:
            try:
                case = op2.cquad4_force[isubcase]
            except KeyError:
                raise KeyError('getting cquad4_force; isubcase=%s; keys=%s' % (
                    isubcase, op2.cquad4_force.keys()))

            eids = unique(case.element)
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)


        card_type = 'CTRIA3'
        if op2.ctria3_stress:
            case = op2.ctria3_stress[isubcase]
            eids = unique(case.element_node[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.ctria3_strain:
            case = op2.ctria3_strain[isubcase]
            eids = unique(case.element_node[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.ctria3_composite_strain:
            case = op2.ctria3_composite_strain[isubcase]
            eids = unique(case.element_layer[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.ctria3_composite_stress:
            case = op2.ctria3_composite_stress[isubcase]
            eids = unique(case.element_layer[:, 0])
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)
        if op2.ctria3_force:
            case = op2.ctria3_force[isubcase]
            eids = unique(case.element)
            for eid in eids:
                assert eid in out[card_type], 'eid=%s eids=%s card_type=%s'  % (eid, out[card_type], card_type)




    def test_op2_dmi(self):
        folder = os.path.abspath(os.path.join(test_path, '..', 'models'))
        bdf_filename = os.path.join(folder, 'matrix', 'matrix.dat')
        op2_filename = os.path.join(folder, 'matrix', 'mymatrix.op2')
        matrices = {
            'A' : True,
            'B' : False,
            'ATB' : False,
            'BTA' : False,
            'MYDOF' : True,
        }
        model = BDF()
        model.read_bdf(bdf_filename)

        dmi_a = model.dmis['A']
        a, rows_reversed, cols_reversed = dmi_a.get_matrix(is_sparse=False, apply_symmetry=False)
        print('model.dmi.A =\n%s' % dmi_a)
        print('model.dmi.A =\n%s' % str(a))
        #return
        op2 = OP2()
        op2.set_additional_matrices_to_read(matrices)
        try:
            op2.read_op2(op2_filename)
            raise RuntimeError('this is wrong...')
        except FatalError:
            # the OP2 doesn't have a trailing zero marker
            pass

        from numpy import dot, array, array_equal
        # M rows, Ncols
        A = array([
            [1., 0.],
            [3., 6.],
            [5., 0.],
            [0., 8.],
        ], dtype='float32')
        B = A
        mydof = array([
            -1.0, 1.0, 1.0, -1.0, 1.0,
            2.0, -1.0, 1.0, 3.0, -1.0, 1.0, 4.0, -1.0,
            1.0, 5.0, -1.0, 1.0, 6.0, -1.0, 2.0, 1.0,
            -1.0, 2.0, 2.0, -1.0, 2.0, 3.0, -1.0, 2.0,
            4.0, -1.0, 2.0, 5.0, -1.0, 2.0, 6.0,
        ])
        BTA = dot(B.T, A)
        ATB = dot(A.T, B)
        ATB_expected = array([
            [35., 18.],
            [18., 100.]
        ], dtype='float32')
        BTA_expected = ATB_expected

        expecteds = [A, ATB, B, BTA, mydof]
        matrix_names = sorted(matrices.keys())

        for table_name, expected in zip(matrix_names, expecteds):
            assert table_name in op2.matrices, table_name


            actual = op2.matrices[table_name].data
            if not array_equal(expected, actual):
                if table_name in model.dmis:
                    dmi = model.dmis[table_name]
                    table_array, rows_reversed, cols_reversed = dmi.get_matrix(is_sparse=False, apply_symmetry=False)
                    #stable_array, rows_reversed, cols_reversed = dmi.get_matrix(is_sparse=True, apply_symmetry=False)
                    print(table_array)
                #print(stable_array)
                msg = 'matrix %s was not read properly\n' % table_name
                msg += 'expected\n%s\n' % expected
                msg += 'actual\n%s' % actual
                print(msg)
                print('==========================')
                #raise RuntimeError(msg)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
