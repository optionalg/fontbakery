# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import pytest

from fontbakery.testrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , ENDTEST
            )

test_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

@pytest.fixture
def font_1():
  # FIXME: find absolute path via the path of this module
  path = 'data/test/cabin/Cabin-Regular.ttf'
  # return TTFont(path)
  return path


@pytest.fixture
def mada_ttFonts():
  paths = [
    "data/test/mada/Mada-Black.ttf",
    "data/test/mada/Mada-ExtraLight.ttf",
    "data/test/mada/Mada-Medium.ttf",
    "data/test/mada/Mada-SemiBold.ttf",
    "data/test/mada/Mada-Bold.ttf",
    "data/test/mada/Mada-Light.ttf",
    "data/test/mada/Mada-Regular.ttf",
  ]
  return [TTFont(path) for path in paths]


@pytest.fixture
def cabin_ttFonts():
  paths = [
    "data/test/cabin/Cabin-BoldItalic.ttf",
    "data/test/cabin/Cabin-Bold.ttf",
    "data/test/cabin/Cabin-Italic.ttf",
    "data/test/cabin/Cabin-MediumItalic.ttf",
    "data/test/cabin/Cabin-Medium.ttf",
    "data/test/cabin/Cabin-Regular.ttf",
    "data/test/cabin/Cabin-SemiBoldItalic.ttf",
    "data/test/cabin/Cabin-SemiBold.ttf"
  ]
  return [TTFont(path) for path in paths]


def change_name_table_id(ttFont, nameID, newEntryString, platEncID=0):
  for i, nameRecord in enumerate(ttFont['name'].names):
    if nameRecord.nameID == nameID and nameRecord.platEncID == platEncID:
      ttFont['name'].names[i].string = newEntryString

def delete_name_table_id(ttFont, nameID):
  delete = []
  for i, nameRecord in enumerate(ttFont['name'].names):
    if nameRecord.nameID == nameID:
      delete.append(i)
  for i in sorted(delete, reverse=True):
    del(ttFont['name'].names[i])


def test_example_testrunner_based(font_1):
  """ This is just an example test. We'll probably need something like
      this setup in a testrunner_test.py testsuite.
      Leave it here for the moment until we implemented a real case.

      This test is run via the testRunner and demonstrate how to get
      (mutable) objects from the conditions cache and change them.

      NOTE: the actual fontbakery tests of conditions should never change
      a condition object.
  """
  from fontbakery.testrunner import TestRunner
  from fontbakery.specifications.googlefonts import specification
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION
  values = dict(fonts=[font_1])
  runner = TestRunner(specification, values, explicit_tests=['com.google.fonts/test/029'])

  print('Test PASS ...')
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status in test_statuses:
      last_test_message = message
    if status == ENDTEST:
     assert message == PASS
     break

  # we could also reuse the `iterargs` that was assigned in the previous
  # for loop, but this here is more explicit
  iterargs = ((u'font', 0),)
  ttFont = runner.get('ttFont', iterargs)

  print('Test failing entry ...')
  # prepare
  change_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION, 'failing entry')
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status in test_statuses:
      last_test_message = message
    if status == ENDTEST:
     assert message == FAIL and last_test_message.code == 'wrong'
     break

  print('Test missing entry ...')
  # prepare
  delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
  # run
  for status, message, (section, test, iterargs) in runner.run():
    if status in test_statuses:
      last_test_message = message
    if status == ENDTEST:
     assert message == FAIL and last_test_message.code == 'missing'
     break


def test_id_001():
  """ Files are named canonically. """
  from fontbakery.specifications.googlefonts import \
                                  check_file_is_named_canonically
  canonical_names = [
    "data/test/cabin/Cabin-Thin.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf",
    "data/test/cabin/Cabin-Light.ttf",
    "data/test/cabin/Cabin-Regular.ttf",
    "data/test/cabin/Cabin-Medium.ttf",
    "data/test/cabin/Cabin-SemiBold.ttf",
    "data/test/cabin/Cabin-Bold.ttf",
    "data/test/cabin/Cabin-ExtraBold.ttf",
    "data/test/cabin/Cabin-Black.ttf",
    "data/test/cabin/Cabin-ThinItalic.ttf",
    "data/test/cabin/Cabin-ExtraLightItalic.ttf",
    "data/test/cabin/Cabin-LightItalic.ttf",
    "data/test/cabin/Cabin-Italic.ttf",
    "data/test/cabin/Cabin-MediumItalic.ttf",
    "data/test/cabin/Cabin-SemiBoldItalic.ttf",
    "data/test/cabin/Cabin-BoldItalic.ttf",
    "data/test/cabin/Cabin-ExtraBoldItalic.ttf",
    "data/test/cabin/Cabin-BlackItalic.ttf"
  ]
  non_canonical_names = [
    "data/test/cabin/Cabin.ttf",
    "data/test/cabin/Cabin-semibold.ttf"
  ]

  print('Test PASS ...')
  for canonical in canonical_names:
    status, message = list(check_file_is_named_canonically(canonical))[-1]
    assert status == PASS

  print('Test FAIL ...')
  for non_canonical in non_canonical_names:
    status, message = list(check_file_is_named_canonically(non_canonical))[-1]
    assert status == FAIL


def test_id_002():
  """ Fonts are all in the same directory. """
  from fontbakery.specifications.googlefonts import \
                                  check_all_files_in_a_single_directory
  same_dir = [
    "data/test/cabin/Cabin-Thin.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  multiple_dirs = [
    "data/test/mada/Mada-Regular.ttf",
    "data/test/cabin/Cabin-ExtraLight.ttf"
  ]
  print('Test PASS with same dir: {}'.format(same_dir))
  status, message = list(check_all_files_in_a_single_directory(same_dir))[-1]
  assert status == PASS

  print('Test FAIL with multiple dirs: {}'.format(multiple_dirs))
  status, message = list(check_all_files_in_a_single_directory(multiple_dirs))[-1]
  assert status == FAIL


# TODO: test_id_003
# TODO: test_id_004
# TODO: test_id_005
# TODO: test_id_006
# TODO: test_id_007


def test_id_008(mada_ttFonts):
  """ Fonts have consistent underline thickness ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_consistent_underline_thickness

  print('Test PASS with good family.')
  status, message = list(check_fonts_have_consistent_underline_thickness(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wronge value in one of the font files:
  value = mada_ttFonts[0]['post'].underlineThickness
  incorrect_value = value + 1
  mada_ttFonts[0]['post'].underlineThickness = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check_fonts_have_consistent_underline_thickness(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_009(mada_ttFonts):
  """ Fonts have consistent PANOSE proportion ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_consistent_PANOSE_proportion

  print('Test PASS with good family.')
  status, message = list(check_fonts_have_consistent_PANOSE_proportion(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bProportion
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bProportion = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check_fonts_have_consistent_PANOSE_proportion(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_010(mada_ttFonts):
  """ Fonts have consistent PANOSE family type ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_consistent_PANOSE_family_type

  print('Test PASS with good family.')
  status, message = list(check_fonts_have_consistent_PANOSE_family_type(mada_ttFonts))[-1]
  assert status == PASS

  # introduce a wrong value in one of the font files:
  value = mada_ttFonts[0]['OS/2'].panose.bFamilyType
  incorrect_value = value + 1
  mada_ttFonts[0]['OS/2'].panose.bFamilyType = incorrect_value

  print('Test FAIL with inconsistent family.')
  status, message = list(check_fonts_have_consistent_PANOSE_family_type(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_011(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal numbers of glyphs ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_equal_numbers_of_glyphs

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(check_fonts_have_equal_numbers_of_glyphs(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs.
  status, message = list(check_fonts_have_equal_numbers_of_glyphs(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_012(mada_ttFonts, cabin_ttFonts):
  """ Fonts have equal glyph names ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_equal_glyph_names

  print('Test PASS with good family.')
  # our reference Cabin family is know to be good here.
  status, message = list(check_fonts_have_equal_glyph_names(cabin_ttFonts))[-1]
  assert status == PASS

  print('Test FAIL with fonts that diverge on number of glyphs.')
  # our reference Mada family is bad here with 407 glyphs on most font files
  # except the Black and the Medium, that both have 408 glyphs (that extra glyph
  # causes the test to fail).
  status, message = list(check_fonts_have_equal_glyph_names(mada_ttFonts))[-1]
  assert status == FAIL


def test_id_013(mada_ttFonts):
  """ Fonts have equal unicode encodings ? """
  from fontbakery.specifications.googlefonts import \
                                  check_fonts_have_equal_unicode_encodings
  from fontbakery.constants import (PLAT_ENC_ID_SYMBOL,
                                    PLAT_ENC_ID_UCS2)
  print('Test PASS with good family.')
  # our reference Mada family is know to be good here.
  status, message = list(check_fonts_have_equal_unicode_encodings(mada_ttFonts))[-1]
  assert status == PASS

  bad_ttFonts = mada_ttFonts
  # introduce mismatching encodings into the first 2 font files:
  for i, encoding in enumerate([PLAT_ENC_ID_SYMBOL,
                                PLAT_ENC_ID_UCS2]):
    for table in bad_ttFonts[i]['cmap'].tables:
      if table.format == 4:
        table.platEncID = encoding

  print('Test FAIL with fonts that diverge on unicode encoding.')
  status, message = list(check_fonts_have_equal_unicode_encodings(bad_ttFonts))[-1]
  assert status == FAIL


def test_id_029(mada_ttFonts):
  """ Check copyright namerecords match license file. """
  from fontbakery.specifications.googlefonts import \
                                  check_copyright_entries_match_license
  from fontbakery.constants import NAMEID_LICENSE_DESCRIPTION

  # Our reference Mada family its copyright name records properly set
  # identifying it as being licensed under the Open Font License
  license = 'OFL.txt'
  wrong_license = 'LICENSE.txt' # Apache

  print('Test PASS with good fonts ...')
  for ttFont in mada_ttFonts:
    status, message = list(check_copyright_entries_match_license(ttFont, license))[-1]
    assert status == PASS

  print('Test with wrong entry values ...')
  for ttFont in mada_ttFonts:
    status, message = list(check_copyright_entries_match_license(ttFont, wrong_license))[-1]
    assert status == FAIL and message.code == 'wrong'

  print('Test with missing copyright namerecords ...')
  for ttFont in mada_ttFonts:
    delete_name_table_id(ttFont, NAMEID_LICENSE_DESCRIPTION)
    status, message = list(check_copyright_entries_match_license(ttFont, license))[-1]
    assert status == FAIL and message.code == 'missing'
