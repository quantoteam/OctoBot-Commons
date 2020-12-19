#  Drakkar-Software OctoBot-Commons
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import os
import shutil
import zipfile
import contextlib
import mock
import octobot_commons.constants as constants
import octobot_commons.profiles as profiles
from octobot_commons.profiles.profile_sharing import _get_unique_profile_folder
import octobot_commons.tests.test_config as test_config

from tests.profiles import profile, get_profile_path


def test_export_profile(profile):
    export_path = "exported"
    exported_file = f"{export_path}.zip"
    tentacles_config = os.path.join(get_profile_path(), "tentacles_config.json")
    spec_tentacles_config = os.path.join(get_profile_path(), "specific_config")
    other_profile = os.path.join(test_config.TEST_FOLDER, "other_profile")
    with _cleaned_tentacles(export_path,
                            exported_file,
                            tentacles_config,
                            dir1=spec_tentacles_config,
                            dir2=other_profile):
        # create fake tentacles config
        shutil.copy(profile.config_file(), tentacles_config)
        os.mkdir(spec_tentacles_config)
        shutil.copy(profile.config_file(), os.path.join(spec_tentacles_config, "t1.json"))
        shutil.copy(profile.config_file(), os.path.join(spec_tentacles_config, "t2.json"))
        with mock.patch.object(os, "remove", mock.Mock()) as remove_mock:
            profiles.export_profile(profile, export_path)
            remove_mock.assert_not_called()
        profiles.export_profile(profile, export_path)
        assert os.path.isfile(exported_file)
        with zipfile.ZipFile(exported_file) as zipped:
            zipped.extractall(other_profile)
        # ensure all files got zipped
        for root, dirs, files in os.walk(profile.path):
            dir_path = os.path.join(other_profile, "specific_config") if "specific_config" in root else other_profile
            assert all(
                os.path.isfile(os.path.join(dir_path, f))
                for f in files
            )


def test_export_profile_with_existing_file(profile):
    export_path = "exported"
    exported_file = f"{export_path}.zip"
    tentacles_config = os.path.join(get_profile_path(), "tentacles_config.json")
    spec_tentacles_config = os.path.join(get_profile_path(), "specific_config")
    other_profile = os.path.join(test_config.TEST_FOLDER, "other_profile")
    with _cleaned_tentacles(export_path,
                            exported_file,
                            tentacles_config,
                            dir1=spec_tentacles_config,
                            dir2=other_profile):
        # create fake tentacles config
        shutil.copy(profile.config_file(), tentacles_config)
        os.mkdir(spec_tentacles_config)
        shutil.copy(profile.config_file(), os.path.join(spec_tentacles_config, "t1.json"))
        shutil.copy(profile.config_file(), os.path.join(spec_tentacles_config, "t2.json"))
        shutil.copy(profile.config_file(), f"{export_path}.{constants.PROFILE_EXPORT_FORMAT}")
        with mock.patch.object(os, "remove", mock.Mock()) as remove_mock:
            profiles.export_profile(profile, export_path)
            remove_mock.assert_called_once_with(f"{export_path}.{constants.PROFILE_EXPORT_FORMAT}")
        assert os.path.isfile(exported_file)
        with zipfile.ZipFile(exported_file) as zipped:
            zipped.extractall(other_profile)
        # ensure all files got zipped
        for root, dirs, files in os.walk(profile.path):
            dir_path = os.path.join(other_profile, "specific_config") if "specific_config" in root else other_profile
            assert all(
                os.path.isfile(os.path.join(dir_path, f))
                for f in files
            )


def test_import_profile(profile):
    export_path = os.path.join(test_config.TEST_FOLDER, "super_profile")
    exported_file = f"{export_path}.zip"
    spec_tentacles_config = os.path.join(get_profile_path(), "specific_config")
    tentacles_config = os.path.join(get_profile_path(), "tentacles_config.json")
    other_profile = os.path.join(constants.USER_PROFILES_FOLDER, "imported_super_profile")
    with _cleaned_tentacles(export_path,
                            exported_file,
                            tentacles_config,
                            dir1=other_profile,
                            dir2=constants.USER_FOLDER,
                            dir3=spec_tentacles_config):
        # create fake tentacles config
        shutil.copy(profile.config_file(), tentacles_config)
        os.mkdir(spec_tentacles_config)
        shutil.copy(profile.config_file(), os.path.join(spec_tentacles_config, "t1.json"))
        shutil.copy(profile.config_file(), os.path.join(spec_tentacles_config, "t2.json"))
        profiles.export_profile(profile, export_path)
        profiles.import_profile(exported_file)
        assert os.path.isdir(os.path.join(constants.USER_PROFILES_FOLDER, "imported_super_profile"))
        # ensure all files got imported
        for root, dirs, files in os.walk(profile.path):
            dir_path = os.path.join(other_profile, "specific_config") if "specific_config" in root else other_profile
            assert all(
                os.path.isfile(os.path.join(dir_path, f))
                for f in files
            )


def test_get_unique_profile_folder(profile):
    assert _get_unique_profile_folder(profile.config_file()) == f"{profile.config_file()}_2"
    other_file = f"{profile.config_file()}_2"
    other_file_2 = f"{profile.config_file()}_3"
    other_file_3 = f"{profile.config_file()}_5"
    with _cleaned_tentacles(other_file, other_file_2, other_file_3):
        shutil.copy(profile.config_file(), other_file)
        assert _get_unique_profile_folder(profile.config_file()) == f"{profile.config_file()}_3"
        shutil.copy(profile.config_file(), other_file_2)
        assert _get_unique_profile_folder(profile.config_file()) == f"{profile.config_file()}_4"
        shutil.copy(profile.config_file(), other_file_3)
        assert _get_unique_profile_folder(profile.config_file()) == f"{profile.config_file()}_4"


@contextlib.contextmanager
def _cleaned_tentacles(*items, **dirs):
    try:
        for item in items:
            if os.path.isfile(item):
                os.remove(item)
        for directory in dirs.values():
            if os.path.isdir(directory):
                shutil.rmtree(directory)
        yield
    finally:
        for item in items:
            if os.path.isfile(item):
                os.remove(item)
        for directory in dirs.values():
            if os.path.isdir(directory):
                shutil.rmtree(directory)