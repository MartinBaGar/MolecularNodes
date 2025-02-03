from bpy.types import Panel


class VIEW3D_PT_Interactions(Panel):
    bl_label = "MN Interactions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MN Interactions"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        interaction_props = scene.interaction_visualiser

        layout.prop(interaction_props, "json_file")
        layout.prop(interaction_props, "object_name")
        layout.operator("object.interaction_visualiser")


class VIEW3D_PT_Interactions_Customisation(Panel):
    bl_label = "Customise bonds"
    bl_idname = "IV_subpanel_1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom Tab"
    bl_parent_id = "VIEW3D_PT_Interactions"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        interaction_props = scene.interaction_visualiser

        layout.label(text="Characteristics")
        layout.prop(interaction_props, "bond_width")
        layout.label(text="Material")
        # layout.prop(interaction_props, "material")
        # layout.prop(interaction_props, "material")


CLASSES = [
    VIEW3D_PT_Interactions,
    VIEW3D_PT_Interactions_Customisation,
]
