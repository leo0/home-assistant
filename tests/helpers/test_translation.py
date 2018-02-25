"""Test the translation helper."""
# pylint: disable=protected-access
import asyncio
from os import path

import homeassistant.helpers.translation as translation
from homeassistant.setup import async_setup_component


def test_flatten():
    """Test the flatten function."""
    data = {
        "parent1": {
            "child1": "data1",
            "child2": "data2",
        },
        "parent2": "data3",
    }

    flattened = translation.flatten(data)

    assert flattened == {
        "parent1.child1": "data1",
        "parent1.child2": "data2",
        "parent2": "data3",
    }


@asyncio.coroutine
def test_component_translation_file(hass):
    """Test the component translation file function."""
    assert (yield from async_setup_component(hass, 'switch', {
        'switch': {'platform': 'test'}
    }))
    assert (yield from async_setup_component(hass, 'test_standalone', {
        'test_standalone'
    }))
    assert (yield from async_setup_component(hass, 'test_package', {
        'test_package'
    }))

    assert path.normpath(translation.component_translation_file(
        'switch.test', 'en')) == path.normpath(hass.config.path(
            'custom_components', 'switch', '.translations', 'test.en.json'))

    assert path.normpath(translation.component_translation_file(
        'test_standalone', 'en')) == path.normpath(hass.config.path(
            'custom_components', '.translations', 'test_standalone.en.json'))

    assert path.normpath(translation.component_translation_file(
        'test_package', 'en')) == path.normpath(hass.config.path(
            'custom_components', 'test_package', '.translations', 'en.json'))


def test_load_translations_files(hass):
    """Test the load translation files function."""
    # Test one valid and one invalid file
    file1 = hass.config.path(
        'custom_components', 'switch', '.translations', 'test.en.json')
    file2 = hass.config.path(
        'custom_components', 'switch', '.translations', 'invalid.json')
    assert translation.load_translations_files([file1, file2]) == {
        file1: {
            'state': {
                'string1': 'Value 1',
                'string2': 'Value 2',
            }
        },
        file2: {},
    }


@asyncio.coroutine
def test_get_translations(hass):
    """Test the get translations helper."""
    translations = yield from translation.async_get_translations(hass, 'en')
    assert translations == {}

    assert (yield from async_setup_component(hass, 'switch', {
        'switch': {'platform': 'test'}
    }))

    translations = yield from translation.async_get_translations(hass, 'en')
    assert translations == {
        'component.switch.state.string1': 'Value 1',
        'component.switch.state.string2': 'Value 2',
    }

    translations = yield from translation.async_get_translations(hass, 'de')
    assert translations == {
        'component.switch.state.string1': 'German Value 1',
        'component.switch.state.string2': 'German Value 2',
    }

    # Test a partial translation
    translations = yield from translation.async_get_translations(hass, 'es')
    assert translations == {
        'component.switch.state.string1': 'Spanish Value 1',
        'component.switch.state.string2': 'Value 2',
    }

    # Test that an untranslated language falls back to English.
    translations = yield from translation.async_get_translations(
        hass, 'invalid-language')
    assert translations == {
        'component.switch.state.string1': 'Value 1',
        'component.switch.state.string2': 'Value 2',
    }