import json


def get_setting(organization, module_label, key):
    """
    Возвращает значение настройки модуля для организации.

    Приоритет:
    1. Переопределение организации (OrganizationModuleSetting)
    2. Значение по умолчанию платформы (ModuleSettingDefinition)
    3. None если настройка не определена вообще

    Использование в модулях:
        from platform_core.module_settings import get_setting
        timeout = get_setting(request.organization, 'reception', 'processing_timeout_hours')
    """
    from platform_core.models import ModuleSettingDefinition, OrganizationModuleSetting

    if organization is not None:
        try:
            override = OrganizationModuleSetting.objects.get(
                organization=organization,
                module=module_label,
                key=key,
            )
            return json.loads(override.value)
        except OrganizationModuleSetting.DoesNotExist:
            pass

    try:
        definition = ModuleSettingDefinition.objects.get(module=module_label, key=key)
        return json.loads(definition.default_value)
    except ModuleSettingDefinition.DoesNotExist:
        return None
