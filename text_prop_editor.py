import bpy
from . import bm_props


class PropEditorSettings(bpy.types.PropertyGroup):
    active = bpy.props.BoolProperty()
    full_data_path = bpy.props.StringProperty(
        name="Data path",
        description="Full path to a structure that has a specific property to edit.")
    attr = bpy.props.StringProperty(name="Property", description="Text property name.")
    pointer = bpy.props.StringProperty()
    apply_text = bpy.props.StringProperty(default="Apply")

    def validate_path(self):
        try:
            prop = eval(self.full_data_path)  # type: bpy.types.bpy_struct
        except:
            return False
        return isinstance(prop, bpy.types.bpy_struct) and str(prop.as_pointer()) == self.pointer

    def copy_to(self, other):
        """ Shallow copy
        :type other: PropEditorSettings
        :rtype: PropEditorSettings
        """
        for key, value in self.items():
            other[key] = value
        return other

    @classmethod
    def register(cls):
        bpy.types.Text.jbeam_flow = bpy.props.PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del bpy.types.Text.jbeam_flow


class EditOperator(bpy.types.Operator):
    """Edit this property in Text Editor"""
    bl_idname = "object.edit_text_prop"
    bl_label = "Edit in Text Editor"
    bl_options = {'REGISTER'}

    settings = bpy.props.PointerProperty(type=PropEditorSettings)  # type: PropEditorSettings

    def execute(self, context):
        try:
            prop = eval(self.settings.full_data_path)  # type: bpy.types.bpy_struct
        except Exception as err:
            self.report({'ERROR'},
                        "Cannot evaluate data path '{}': {}".format(self.settings.full_data_path, err))
            return {'CANCELLED'}

        text = bpy.data.texts.new("Text Property Editor")
        text.from_string(getattr(prop, self.settings.attr))
        settings = self.settings.copy_to(text.jbeam_flow)
        settings.pointer = str(prop.as_pointer())
        settings.active = True

        # switch first text editor space
        for area in context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.spaces.active.text = text
                break
        else:
            self.report({'INFO'}, "See '{}' in the text editor".format(text.name))

        return {'FINISHED'}


class ApplyOperator(bpy.types.Operator):
    """Apply text to property"""
    bl_idname = "text.apply_to_prop"
    bl_label = "Apply"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.edit_text and context.edit_text.jbeam_flow and context.edit_text.jbeam_flow.active

    def execute(self, context):
        settings = context.edit_text.jbeam_flow  # type: PropEditorSettings
        if not settings.validate_path():
            self.report({'ERROR'}, "Cannot apply changes: data path has been changed "
                                   "or 'Undo/Redo' was used outside a Text Editor.")
            return {'CANCELLED'}
        else:
            prop = eval(settings.full_data_path)  # type: bpy.types.bpy_struct
            try:
                setattr(prop, settings.attr, context.edit_text.as_string())
                # exception suppressing workaround
                if bm_props.last_error:
                    raise bm_props.last_error
            except Exception as err:
                self.report({'ERROR'}, "Cannot apply changes: {}".format(err))
                return {'CANCELLED'}
            else:
                self.report({'INFO'}, "Applied to active element")
                return {'FINISHED'}


class TextPropEditPanel(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Text Property Editor"

    @classmethod
    def poll(cls, context):
        return context.edit_text and context.edit_text.jbeam_flow and context.edit_text.jbeam_flow.active

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        settings = context.edit_text.jbeam_flow  # type: PropEditorSettings
        # layout.prop(settings, 'active')
        layout.prop(settings, 'full_data_path', icon='RNA')
        layout.prop(settings, 'attr', icon='RNA')

        # layout.prop(settings, 'pointer')
        layout.operator(ApplyOperator.bl_idname,
                        text=settings.apply_text,
                        icon='FILE_TICK' if settings.validate_path() else 'ERROR')


classes = (
    PropEditorSettings,
    EditOperator,
    ApplyOperator,
    TextPropEditPanel,
)
