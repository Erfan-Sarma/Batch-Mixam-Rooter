bl_info = {
    "name": "MixamoRooter (Bulk)",
    "author": "Erfan",
    "version": (2, 8),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > MixamoRooter",
    "description": "Batch process Mixamo characters and animations with proper root motion and seamless hip loop fixing for UE5",
    "category": "Animation",
}

import bpy
import os
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, Panel

class MIXAMO_OT_BatchProcessCharacters(Operator):
    bl_idname = "mixamo.batch_process_characters"
    bl_label = "Bulk Fix Characters"
    bl_description = "Select multiple Mixamo character FBX files to inject root bones and export cleanly"

    directory: StringProperty(subtype='DIR_PATH')
    files: CollectionProperty(type=bpy.types.OperatorFileListElement)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        out_dir = context.scene.mixamo_output_dir
        if not out_dir:
            self.report({'ERROR'}, "Please select an Output Directory first!")
            return {'CANCELLED'}

        success_count = 0
        for file_elem in self.files:
            filepath = os.path.join(self.directory, file_elem.name)
            
            # Context-safe scene clearing without bpy.ops
            for obj in list(context.scene.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            
            # Import FBX
            bpy.ops.import_scene.fbx(filepath=filepath)
            
            # Find Armature
            armature = next((obj for obj in context.scene.objects if obj.type == 'ARMATURE'), None)
            if armature:
                context.view_layer.objects.active = armature
                armature.select_set(True)
                
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = armature.data.edit_bones
                
                hips_name = next((b.name for b in edit_bones if 'hips' in b.name.lower()), None)
                if hips_name:
                    hips_bone = edit_bones.get(hips_name)
                    if 'root' in edit_bones:
                        edit_bones.remove(edit_bones.get('root'))
                        
                    root_bone = edit_bones.new('root')
                    root_bone.head = (0.0, 0.0, 0.0)
                    root_bone.tail = (0.0, 0.0, 1.0)
                    hips_bone.parent = root_bone
                    
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Export modified FBX
                out_path = os.path.join(out_dir, file_elem.name)
                bpy.ops.export_scene.fbx(filepath=out_path, use_selection=False, add_leaf_bones=False)
                success_count += 1

            # Cleanup memory data blocks to prevent duplication
            for mesh in list(bpy.data.meshes):
                bpy.data.meshes.remove(mesh)
            for arm in list(bpy.data.armatures):
                bpy.data.armatures.remove(arm)

        self.report({'INFO'}, f"Successfully processed {success_count} character(s)!")
        return {'FINISHED'}


class MIXAMO_OT_BatchProcessAnimations(Operator):
    bl_idname = "mixamo.batch_process_animations"
    bl_label = "Bulk Fix Animations"
    bl_description = "Select multiple Mixamo animation FBX files to add root motion cleanly with seamless hip looping"

    directory: StringProperty(subtype='DIR_PATH')
    files: CollectionProperty(type=bpy.types.OperatorFileListElement)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        out_dir = context.scene.mixamo_output_dir
        if not out_dir:
            self.report({'ERROR'}, "Please select an Output Directory first!")
            return {'CANCELLED'}

        success_count = 0
        for file_elem in self.files:
            filepath = os.path.join(self.directory, file_elem.name)
            
            # Context-safe scene clearing without bpy.ops
            for obj in list(context.scene.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            
            # Import FBX
            bpy.ops.import_scene.fbx(filepath=filepath)
            
            # Find Armature
            armature = next((obj for obj in context.scene.objects if obj.type == 'ARMATURE'), None)
            if armature:
                context.view_layer.objects.active = armature
                armature.select_set(True)
                
                # 1. Edit Mode: Create Root Bone
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = armature.data.edit_bones
                hips_name = next((b.name for b in edit_bones if 'hips' in b.name.lower()), None)
                
                if hips_name:
                    hips_bone = edit_bones.get(hips_name)
                    if 'root' in edit_bones:
                        edit_bones.remove(edit_bones.get('root'))
                        
                    root_bone = edit_bones.new('root')
                    root_bone.head = (0.0, 0.0, 0.0)
                    root_bone.tail = (0.0, 0.0, 1.0)
                    hips_bone.parent = root_bone
                    
                    # 2. Pose Mode: Map Root Motion & Fix Hip Y Loop Snapping
                    bpy.ops.object.mode_set(mode='POSE')
                    action = armature.animation_data.action if armature.animation_data else None
                    
                    if action:
                        # Lock scene frame range precisely to action range to prevent extra frames
                        start_f = int(action.frame_range[0])
                        end_f = int(action.frame_range[1])
                        context.scene.frame_start = start_f
                        context.scene.frame_end = end_f
                        
                        hips_path = f'pose.bones["{hips_name}"].location'
                        root_path = 'pose.bones["root"].location'
                        
                        def get_or_create_fcurve(path, index):
                            if hasattr(action, "fcurve_ensure_for_datablock"):
                                return action.fcurve_ensure_for_datablock(armature, path, index=index)
                            else:
                                return action.fcurves.find(path, index=index) or action.fcurves.new(path, index=index)

                        fc_hips_x = get_or_create_fcurve(hips_path, 0)
                        fc_hips_y = get_or_create_fcurve(hips_path, 1) # Hips Y location
                        fc_hips_z = get_or_create_fcurve(hips_path, 2)
                        fc_root_x = get_or_create_fcurve(root_path, 0)
                        fc_root_y = get_or_create_fcurve(root_path, 1)
                        
                        # Transfer Hips X -> Root X
                        if fc_hips_x and len(fc_hips_x.keyframe_points) > 0 and fc_root_x:
                            fc_root_x.keyframe_points.clear()
                            for pt in fc_hips_x.keyframe_points:
                                fc_root_x.keyframe_points.insert(pt.co[0], pt.co[1])
                            fc_hips_x.keyframe_points.clear()
                            fc_hips_x.keyframe_points.insert(float(start_f), 0.0)
                            
                        # Transfer Hips Z -> Root Y
                        if fc_hips_z and len(fc_hips_z.keyframe_points) > 0 and fc_root_y:
                            fc_root_y.keyframe_points.clear()
                            for pt in fc_hips_z.keyframe_points:
                                fc_root_y.keyframe_points.insert(pt.co[0], pt.co[1])
                            fc_hips_z.keyframe_points.clear()
                            fc_hips_z.keyframe_points.insert(float(start_f), 0.0)
                            
                        # Fix Hips Y location loop snapping (align first and last keyframe values on the hip bone)
                        if fc_hips_y and len(fc_hips_y.keyframe_points) > 1:
                            first_val = fc_hips_y.keyframe_points[0].co[1]
                            fc_hips_y.keyframe_points[-1].co[1] = first_val
                            
                        action.update_tag()
                        
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Export processed animation FBX with exact frame bounds
                out_path = os.path.join(out_dir, file_elem.name)
                bpy.ops.export_scene.fbx(
                    filepath=out_path,
                    use_selection=False,
                    add_leaf_bones=False,
                    bake_anim=True,
                    bake_anim_use_all_actions=False,
                    bake_anim_use_nla_strips=False
                )
                success_count += 1

            # CRUCIAL: Purge imported actions, meshes, and armatures from memory to prevent accumulation
            for action in list(bpy.data.actions):
                bpy.data.actions.remove(action)
            for mesh in list(bpy.data.meshes):
                bpy.data.meshes.remove(mesh)
            for arm in list(bpy.data.armatures):
                bpy.data.armatures.remove(arm)

        self.report({'INFO'}, f"Successfully processed {success_count} animation(s) cleanly!")
        return {'FINISHED'}


class VIEW3D_PT_MixamoRootPanel(Panel):
    bl_label = "MixamoRooter (Bulk)"
    bl_idname = "VIEW3D_PT_mixamo_root_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MixamoRooter"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Output Directory", icon='FILE_FOLDER')
        layout.prop(scene, "mixamo_output_dir", text="")
        
        layout.separator()
        
        layout.label(text="Bulk Batch Processing", icon='AUTOMERGE_ON')
        
        row = layout.row(align=True)
        row.operator("mixamo.batch_process_characters", icon='OUTLINER_OB_MESH', text="Bulk Fix Characters")
        
        row = layout.row(align=True)
        row.operator("mixamo.batch_process_animations", icon='ANIM', text="Bulk Fix Animations")


classes = (
    MIXAMO_OT_BatchProcessCharacters,
    MIXAMO_OT_BatchProcessAnimations,
    VIEW3D_PT_MixamoRootPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mixamo_output_dir = StringProperty(
        name="Output Directory",
        subtype='DIR_PATH',
        description="Select folder where processed FBX files will be saved"
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mixamo_output_dir

if __name__ == "__main__":
    register()