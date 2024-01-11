import bpy
import numpy as np
import pytest
import itertools
import tempfile
import molecularnodes as mn
from .constants import (
    test_data_directory,
    codes,
    attributes
)
from .utils import get_verts, apply_mods, sample_attribute_to_string

mn.unregister()
mn.register()

styles = ['preset_1', 'cartoon', 'ribbon',
          'spheres', 'surface', 'ball_and_stick']


def useful_function(snapshot, style, code, assembly, cache_dir=None):
    obj = mn.io.pdb.load(
        code, style=style, build_assembly=assembly, cache_dir=cache_dir)
    node = mn.blender.nodes.get_style_node(obj)
    eevee = node.inputs.get('EEVEE')
    if eevee:
        eevee.default_value = True

    mn.blender.nodes.realize_instances(obj)
    if style == 'cartoon' and code == '1BNA':
        with pytest.raises(RuntimeError):
            apply_mods(obj)
    else:
        apply_mods(obj)
        for att in attributes:
            snapshot.assert_match(
                sample_attribute_to_string(obj, att),
                f"{att}.txt"
            )


with tempfile.TemporaryDirectory() as temp_dir:
    @pytest.mark.parametrize("assembly, code, style", itertools.product([False], codes, styles))
    def test_style_1(snapshot, assembly, code, style):
        useful_function(snapshot, style, code, assembly, cache_dir=temp_dir)

    # have to test a subset of styles with the biological assembly.
    # testing some of the heavier styles run out of memory and fail on github actions
    @pytest.mark.parametrize("assembly, code, style", itertools.product([True], codes, ['cartoon', 'surface', 'ribbon']))
    def test_style_2(snapshot, assembly, code, style):
        useful_function(snapshot, style, code, assembly, cache_dir=temp_dir)

    @pytest.mark.parametrize("code, format", itertools.product(codes, ['mmtf', 'cif', 'pdb']))
    def test_download_format(code, format):
        mol = mn.io.pdb.load(code, format=format, style=None)
        scene = bpy.context.scene
        scene.MN_pdb_code = code
        scene.MN_import_node_setup = False
        scene.MN_import_format_download = format
        names = [o.name for o in bpy.data.objects]
        bpy.ops.mn.import_protein_fetch()

        for o in bpy.data.objects:
            if o.name not in names:
                mol2 = o

        def verts(object):
            return mn.blender.obj.get_attribute(object, 'position')
        assert np.isclose(verts(mol), verts(mol2)).all()


def test_local_pdb(snapshot):
    files = [test_data_directory / f"1l58.{ext}" for ext in ['cif', 'pdb']]
    obj1, obj2 = map(mn.io.local.load, files)
    obj3 = mn.io.pdb.load('1l58')
    verts_1, verts_2, verts_3 = map(lambda x: get_verts(
        x, apply_modifiers=False), [obj1, obj2, obj3])
    assert verts_1 == verts_2
    assert verts_1 == verts_3
    snapshot.assert_match(verts_1, '1L58_verts.txt')


def test_rcsb_nmr(snapshot):
    CODE = "2M6Q"
    obj = mn.io.pdb.load(CODE)
    coll_frames = bpy.data.collections[f"{CODE}_frames"]
    assert len(coll_frames.objects) == 10
    assert obj.modifiers['MolecularNodes'].node_group.nodes['MN_animate_value'].inputs['To Max'].default_value == 9

    verts = get_verts(obj, apply_modifiers=False)
    snapshot.assert_match(verts, 'rcsb_nmr_2M6Q.txt')


def test_load_small_mol(snapshot):
    file = test_data_directory / "ASN.cif"
    obj = mn.io.local.load(file)
    verts = get_verts(obj, apply_modifiers=False)
    snapshot.assert_match(verts, 'asn_atoms.txt')

    bond_types = mn.blender.obj.get_attribute(obj, 'bond_type')
    edges = ''.join([str(bond_type) for bond_type in bond_types])
    snapshot.assert_match(edges, 'asn_edges.txt')


def test_rcsb_cache(snapshot):
    from pathlib import Path
    import tempfile
    import os
    # we want to make sure cached files are freshly downloaded, but
    # we don't want to delete our entire real cache
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_cache = Path(temp_dir)

        # Run the test
        obj_1 = mn.io.pdb.load('6BQN', style='cartoon', cache_dir=test_cache)
        file = os.path.join(test_cache, '6BQN.mmtf')
        assert os.path.exists(file)

        obj_2 = mn.io.pdb.load('6BQN', style='cartoon', cache_dir=test_cache)
        assert get_verts(obj_1) == get_verts(obj_2)
