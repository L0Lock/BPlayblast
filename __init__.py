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

bl_info = {
    "name": "BPlayblast",
    "author": "Loïc Dautry & Luciano Muñoz & Cristian Hasbun",
    "description": "Gives playblast tools for fast animation previews.",
    "blender": (2, 93, 1),
    "version": (0, 0, 1),
    "location": "Properties Editor > Output Tab > BPlayblast Pannel",
    "warning": "Beta version, expect unwanted behaviors and frequent changes",
    "category": "Animation",
    "support": "COMMUNITY"
}

import os.path

import bpy
from bpy.props import *

#DEBUGGER
#import pudb
#_MODULE_SOURCE_CODE = bpy.data.texts[__file__.split('/')[-1]].as_string()
#_MODULE_SOURCE_CODE = bpy.data.texts[os.path.basename(__file__)].as_string()


class BoomProps(bpy.types.PropertyGroup):

    global_toggle: BoolProperty(
        name = 'Global',
        description = 'Same boomsmash settings for all scenes in file.',
        default = False)

    #twm.image_settings = bpy.types.ImageFormatSettings(
    #                        bpy.context.scene.render.image_settings)

    scene_cam: BoolProperty(
        name = 'Active Camera',
        description = 'Always renders from the active camera that\'s set in the Scene properties')

    incremental: BoolProperty(
        name = 'Incremental',
        description = 'Save incremental boomsmashes.',
        default = False)

    use_stamp: BoolProperty(
        name = 'Stamp',
        description = 'Turn on stamp (uses settings from render properties).',
        default = False)    
        
    transparent: BoolProperty(
        name = 'Transparent',
        description = 'Make background transparent (only for formats that support alpha, i.e.: .png).',
        default = False)
        
    autoplay: BoolProperty(
        name = 'Autoplay',
        description = 'Automatically play boomsmash after making it.',
        default = False)              
        
    unsimplify: BoolProperty(
        name = 'Unsimplify',
        description = "Boomsmash with the subdivision surface levels at it's render settings.",
        default = False)
        
    overlays: BoolProperty(
        name = 'Overlays',
        description = 'Make overlays visible during boomsmash.',
        default = False)
        
    frame_skip: IntProperty(
        name = 'Skip Frames',
        description = 'Number of frames to skip',
        default = 0,
        min = 0)        

    resolution_percentage: IntProperty(
        name = 'Resolution Percentage',
        description = 'define a percentage of the Render Resolution to make your boomsmash',
        default = 50,
        min = 0,
        soft_max = 100,
        max = 1000)

    #DEBUG
    #pu.db

    dirname: StringProperty(
        name = '',
        description = 'Folder where your boomsmash will be stored',
        default = bpy.app.tempdir,
        subtype = 'DIR_PATH')  

    filename: StringProperty(
        name = '',
        description = 'Filename where your boomsmash will be stored',
        default = 'Boomsmash',
        subtype = 'FILE_NAME')  


class setDirname(bpy.types.Operator):
    bl_idname = 'bs.setdirname'
    bl_label = 'BoomsmashDirname'
    bl_description = 'boomsmash use blendfile directory'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        cs = context.scene
        # cs.boom_props.dirname = os.path.dirname(bpy.data.filepath)
        if bpy.data.is_saved == True:
            cs.boom_props.dirname = "\\"
        else: cs.boom_props.dirname = os.path.dirname(bpy.data.filepath)
        return {'FINISHED'} 
            

class setFilename(bpy.types.Operator):
    bl_idname = 'bs.setfilename'
    bl_label = 'BoomsmashFilename'
    bl_description = 'boomsmash use blendfile name _ scene name'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        cs = context.scene
        blend_name = os.path.basename(
                      os.path.splitext(bpy.data.filepath)[0])
        cs.boom_props.filename = blend_name + '_' + bpy.context.scene.name
        return {'FINISHED'} 
    

class DoBoom(bpy.types.Operator):
    bl_idname = 'bs.doboom'
    bl_label = 'Boomsmash'
    bl_description = 'Start boomsmash, use, enjoy, think about donate ;)'
    bl_options = {'REGISTER'}

    def execute(self, context): 
        cs = context.scene
        wm = context.window_manager
        rd = context.scene.render
        sd = context.space_data

        if wm.boom_props.global_toggle:
            boom_props = wm.boom_props
        else:
            boom_props = cs.boom_props

        #pu.db

        # settings backup
        old_use_stamp = rd.use_stamp
        old_overlays = sd.overlay.show_overlays
        old_simplify = rd.use_simplify 
        old_filepath = rd.filepath
        old_film_transparent = rd.film_transparent
        # old_image_settings = rd.image_settings
        old_resolution_percentage = rd.resolution_percentage
        old_frame_step = cs.frame_step

        # original settings affection
        rd.use_stamp = boom_props.use_stamp
        sd.overlay.show_overlays = boom_props.overlays
        if boom_props.unsimplify:
            rd.use_simplify = False
        rd.filepath = cs.boom_props.dirname + cs.boom_props.filename
        rd.film_transparent = 1 if boom_props.transparent else 0

        #rd.image_settings = boom_props.image_settings
        rd.resolution_percentage = boom_props.resolution_percentage
        cs.frame_step = boom_props.frame_skip + 1
        view_pers = context.area.spaces[0].region_3d.view_perspective
        if boom_props.scene_cam and view_pers != 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
           
        
        # Rendering goes brrrr!!
        bpy.ops.render.opengl(animation = True)
        if boom_props.autoplay:
            bpy.ops.render.play_rendered_anim()
 
        # settings restoration
        rd.use_stamp = old_use_stamp
        sd.overlay.show_overlays = old_overlays
        rd.use_simplify = old_simplify
        rd.filepath = old_filepath
        rd.film_transparent = old_film_transparent
        #rd.image_settings = old_image_settings
        rd.resolution_percentage = old_resolution_percentage
        context.scene.frame_step = old_frame_step
        if boom_props.scene_cam and view_pers != 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective = view_pers

        return {'FINISHED'}  
    
    #def cancel(self, context):
    #    print('brrr cancel brrr brrrr!!!')
    #    return {'CANCELLED'}  



def draw_boomsmash_panel(context, layout):
    col = layout.column(align = True)
    cs = context.scene
    wm = context.window_manager 
    rd = context.scene.render

    if wm.boom_props.global_toggle:
        boom_props = wm.boom_props
    else:
        boom_props = cs.boom_props
    
    split = col.split()
    subcol = split.column()
    #subcol.prop(boom_props, 'incremental')
    subcol.prop(boom_props, 'use_stamp')
    subcol.prop(boom_props, 'overlays')
    subcol.prop(boom_props, 'scene_cam')

    subcol = split.column()
    subcol.prop(boom_props, 'transparent')
    subcol.prop(boom_props, 'autoplay')
    subcol.prop(boom_props, 'unsimplify')
    
    # Old layout, need a way to have all onelined and disabled if preview range disabled
    # col.separator()
    # col.label(text = 'Use preview range:')
    # sub = col.split()
    # subrow = sub.row(align = True)
    # subrow.prop(context.scene, 'use_preview_range', text = 'Use preview range:')
    # subrow = col.split(align = True)
    # subrow.enabled = context.scene.use_preview_range # truc qui grise
    # subrow.prop(context.scene, 'frame_preview_start', text = 'Start')
    # subrow.prop(boom_props, 'frame_skip', text = 'Skip')
    # subrow.prop(context.scene, 'frame_preview_end', text = 'End')
    # col.separator()

    # Alt layout, not onelined but working and better than nothing
    # col.separator()
    # sub = col.split()
    # subrow = sub.row(align = True)
    # subrow.prop(context.scene, 'use_preview_range', text = 'Use preview range:')
    # subrow = col.split(align = True)
    # subrow.enabled = context.scene.use_preview_range # truc qui grise
    # subrow.prop(context.scene, 'frame_preview_start', text = 'Start')
    # subrow.prop(boom_props, 'frame_skip', text = 'Skip')
    # subrow.prop(context.scene, 'frame_preview_end', text = 'End')
    # col.separator()

    # New layout, insipred from Blender's timeline
    col.separator()
    sub = col.split()
    subrow = sub.row(align = True)
    subrow.prop(context.scene, 'use_preview_range', text = '')
    subrow.scale_x = 0.8
    if not context.scene.use_preview_range:
        subrow.prop(context.scene, "frame_start", text="Start")
        subrow.prop(boom_props, 'frame_skip', text = 'Skip')
        subrow.prop(context.scene, "frame_end", text="End")
    else:
        subrow.prop(context.scene, "frame_preview_start", text="Alt Start")
        subrow.prop(boom_props, 'frame_skip', text = 'Skip')
        subrow.prop(context.scene, "frame_preview_end", text="Alt End")
    col.separator()

    # ===== Blender's Playback control Reference =====
    # row = layout.row(align=True)
    #     row.prop(scene, "use_preview_range", text="", toggle=True)
    #     sub = row.row(align=True)
    #     sub.scale_x = 0.8
    #     if not scene.use_preview_range:
    #         sub.prop(scene, "frame_start", text="Start")
    #         sub.prop(scene, "frame_end", text="End")
    #     else:
    #         sub.prop(scene, "frame_preview_start", text="Start")
    #         sub.prop(scene, "frame_preview_end", text="End")
    
    final_res_x = (rd.resolution_x * boom_props.resolution_percentage) / 100
    final_res_y = (rd.resolution_y * boom_props.resolution_percentage) / 100
    col.label(text = 'Final Resolution: {} x {}'.format(str(final_res_x)[:-2], str(final_res_y)[:-2]))
    col.prop(boom_props, 'resolution_percentage', slider = True )
    
    col.separator()
    
    #col.label(text = 'Output Format:')
    #col.template_image_settings(wm.image_settings, color_management = False)

    col.label(text = 'Destination folder:')
    row = col.row()
    row.prop(cs.boom_props, 'dirname')
    row.operator('bs.setdirname', text = '', icon = 'FILE_FOLDER')
    col.separator()
    col.label(text = 'Filename:')
    row = col.row()
    row.prop(cs.boom_props, 'filename')
    row.operator('bs.setfilename', text = '', icon = 'FILE_BLEND')
    

class VIEW3D_PT_tools_animation_boomsmash(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'
    # bl_context = 'objectmode'
    bl_label = ' '
    
    def draw_header(self, context):
        DoBTN = self.layout
        DoBTN.operator('bs.doboom', text = 'BoomSmash', icon = 'RENDER_ANIMATION')
        DoBTN.prop(context.window_manager.boom_props, 'global_toggle')
        #DoBTN.animation = True

    def draw(self, context):
        layout = self.layout
        draw_boomsmash_panel(context, layout)


# DISABLED -- examining if needed to have different panels fo interaction modes
# class VIEW3D_PT_tools_pose_animation_boomsmash(bpy.types.Panel):
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'View'
#     bl_context = 'posemode'
#     bl_label = ' '
  
#     def draw_header(self, context):
#         DoBTN = self.layout
#         DoBTN.operator('bs.doboom', text = 'BoomSmash', icon = 'RENDER_ANIMATION')
#         DoBTN.prop(context.window_manager.boom_props, 'global_toggle')

#     def draw(self, context):
#         layout = self.layout
#         draw_boomsmash_panel(context, layout)
        
#############################################################################################
###########################     REGISTRATION GOES BRRRR     #################################
#############################################################################################


# List of the name of the classes inherited from Blender types like AddonPreferences, Operator, Panel etc
# order matters, e.g. if those operators depend on MyPropertyGroup
classes = (
    BoomProps,
    setDirname,
    setFilename,
    DoBoom,
    # VIEW3D_PT_tools_pose_animation_boomsmash,
    VIEW3D_PT_tools_animation_boomsmash
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.boom_props = PointerProperty(
            type = BoomProps, name = 'BoomSmash Properties', description = '')

    bpy.types.WindowManager.boom_props = PointerProperty(
            type = BoomProps, name = 'BoomSmash Global Properties', description = '')

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)



# def register():
#     bpy.utils.register_module(__name__)

#     bpy.types.Scene.boom_props = PointerProperty(
#             type = BoomProps, name = 'BoomSmash Properties', description = '')

#     bpy.types.WindowManager.boom_props = PointerProperty(
#             type = BoomProps, name = 'BoomSmash Global Properties', description = '')


# def unregister():
#     bpy.utils.unregister_module(__name__)
#     del bpy.types.Scene.boom_props
#     del bpy.types.WindowManager.boom_props


# if __name__ == '__main__':
#     register()
#     #unregister()
#     print('script goes brrr')