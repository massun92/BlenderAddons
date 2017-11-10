bl_info = {
    "name": "Steel University",
    "author": "Steel University",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "Search",
    "description": "Add tools for Steel University Pipeline",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }


import bpy
import os

# Sumo las propiedades
class PostFixChannelsSettings(bpy.types.PropertyGroup):
    albedo = bpy.props.StringProperty(default="_AT")
    metallic = bpy.props.StringProperty(default="_MS")
    normal = bpy.props.StringProperty(default="_NM")
    emission = bpy.props.StringProperty(default="_EM")

bpy.utils.register_class(PostFixChannelsSettings)

bpy.types.Scene.su_settings = \
    bpy.props.PointerProperty(type=PostFixChannelsSettings)


def add_object(self, context):
    os.chdir(os.path.dirname(bpy.data.filepath)+"/IMAGES")

    for ob in bpy.context.selected_objects:  
        ms  = ob.active_material
        iPos = 0
        #Remuevo todo lo que no sea Outputs
        for node in ms.node_tree.nodes:
            if node.type != "OUTPUT_MATERIAL":
                ms.node_tree.nodes.remove(node)
        #Output
        mo = ms.node_tree.nodes["Material Output"]
        moPos = mo.location
        #Principled
        principled = ms.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        principled.location = (moPos[0]-300,moPos[1])
        ms.node_tree.links.new(principled.outputs["BSDF"],mo.inputs['Surface']) 
        
        for texture in os.listdir():            
            if ms.name in texture:                  
                inChannel = False              
                print(ms.name+"   "+texture)  
                bpy.data.images.load(os.path.join(os.path.dirname(bpy.data.filepath)+"/IMAGES",texture))
                imageNode = ms.node_tree.nodes.new("ShaderNodeTexImage")
                imageNode.image = bpy.data.images[texture]
                imageNode.location = (-1200,iPos)
                #conexiones
                if texture.count("_AT"):
                    ms.node_tree.links.new(imageNode.outputs["Color"],principled.inputs['Base Color'])   
                    imageNode.location = (moPos[0]-900,moPos[1]+200)    
                    inChannel = True 
                if texture.count("_MS"):
                    ms.node_tree.links.new(imageNode.outputs["Color"],principled.inputs['Metallic'])  
                    imageNode.location = (moPos[0]-900,moPos[1]-200)  
                    invert = ms.node_tree.nodes.new("ShaderNodeInvert")    
                    invert.location = (moPos[0]-600,moPos[1]-300)  
                    ms.node_tree.links.new(imageNode.outputs["Color"],invert.inputs['Color'])   
                    ms.node_tree.links.new(invert.outputs["Color"],principled.inputs['Roughness'])    
                    inChannel = True                                                      
                if texture.count("_NM"):
                    imageNode.location = (moPos[0]-900,moPos[1]-500)
                    normalMap = ms.node_tree.nodes.new("ShaderNodeNormalMap")
                    normalMap.location = (moPos[0]-600,moPos[1]-500) 
                    ms.node_tree.links.new(normalMap.outputs["Normal"],principled.inputs['Normal']) 
                    ms.node_tree.links.new(imageNode.outputs["Color"],normalMap.inputs['Color']) 
                    imageNode.color_space="NONE"   
                    inChannel = True                     
                if texture.count("_EM"):
                    imageNode.location = (moPos[0],moPos[1]-300)
                    add = ms.node_tree.nodes.new("ShaderNodeAddShader")
                    add.location = (moPos[0],moPos[1])
                    moPos[0] += 300
                    ms.node_tree.links.new(add.outputs[0],mo.inputs[0]) 
                    ms.node_tree.links.new(principled.outputs[0],add.inputs[0]) 
                    ms.node_tree.links.new(imageNode.outputs[0],add.inputs[1]) 
                    imageNode.color_space="NONE"    
                    inChannel = True 
                if inChannel == False:
                    iPos -= 200    
            
    bpy.ops.file.make_paths_relative()


class SuSetMaterial(bpy.types.Operator):
    """SU Set Material"""
    bl_idname = "material.su_set_material"
    bl_label = "SU Set Material"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        add_object(self, context)

        return {'FINISHED'}

#Object to Material
class SuSetMaterialName(bpy.types.Operator):
    """SU Material Name"""
    bl_idname = "material.su_material_name"
    bl_label = "SU Material Name"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        for ob in bpy.context.selected_objects:
            ob.material_slots[0].material.name = ob.name

        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Add Object",
        icon='PLUGIN')




def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
