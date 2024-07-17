# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.app.handlers import frame_change_post, load_post, save_post

from . import entities, operators, props, session, ui
from .ui import pref
from .ui.node_menu import MN_add_node_menu
from .ui.panel import MN_PT_Scene, pt_object_context, change_style_node_menu

all_classes = (
    ui.CLASSES
    + operators.CLASSES
    + entities.CLASSES
    + [
        props.MolecularNodesObjectProperties,
        MN_PT_Scene,
    ]
    + pref.CLASSES
    + session.CLASSES
)


def _test_register():
    try:
        register()
    except Exception:
        unregister()
        register()


def register():
    # register all of the import operators
    for op in all_classes:
        try:
            bpy.utils.register_class(op)
        except Exception:
            # print(e)
            pass

    bpy.types.NODE_MT_add.append(MN_add_node_menu)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(pt_object_context)
    bpy.types.NODE_MT_context_menu.prepend(change_style_node_menu)

    save_post.append(session._pickle)
    load_post.append(session._load)
    frame_change_post.append(entities.trajectory.handlers.update_trajectories)

    bpy.types.Scene.MNSession = session.MNSession()
    bpy.types.Object.mn = bpy.props.PointerProperty(
        type=props.MolecularNodesObjectProperties
    )
    bpy.types.Object.mn_trajectory_selections = bpy.props.CollectionProperty(
        type=entities.trajectory.selections.TrajectorySelectionItem
    )


def unregister():
    for op in all_classes:
        try:
            bpy.utils.unregister_class(op)
        except Exception:
            # print(e)
            pass

    bpy.types.NODE_MT_add.remove(MN_add_node_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(pt_object_context)
    bpy.types.NODE_MT_context_menu.remove(change_style_node_menu)

    save_post.remove(session._pickle)
    load_post.remove(session._load)
    frame_change_post.remove(entities.trajectory.handlers.update_trajectories)
    del bpy.types.Scene.MNSession
    del bpy.types.Object.mn
    del bpy.types.Object.mn_trajectory_selections
