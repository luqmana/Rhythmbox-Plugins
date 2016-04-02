
# Conf.py
#
# Copyright (C) 2008 - Teemu Kallio <teemu.kallio@cs.helsinki.fi>
#				2009-2010 - Floreal Morandat <morandat AT lirmm DOT fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import gi; gi.require_version('GConf', '2.0')
from gi.repository import GConf, Gst

EQUALIZER_GCONF_PREFIX = '/apps/rhythmbox/plugins/equalizer'
EQUALIZER_PRESET = 'preset'
EQUALIZER_ENABLED = 'enabled'

class Config:
  def __init__(self):

    self.gconf_keys = [	'band0',
        'band1',
        'band2',
        'band3',
        'band4',
        'band5',
        'band6',
        'band7',
        'band8',
        'band9']

    self.gconf = GConf.Client.get_default()
    self.config = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # Create default preset
    if not self.gconf.dir_exists(EQUALIZER_GCONF_PREFIX + '/default'):
      for i in range(0, 10):
        self.gconf.set_float(self.make_path(self.gconf_keys[i], 'default'), self.config[i])

    self.enabled = self.gconf.get_bool(EQUALIZER_GCONF_PREFIX+'/'+EQUALIZER_ENABLED)
    if self.enabled is None:
      self.enabled = True

    if self.gconf.get_string(EQUALIZER_GCONF_PREFIX+'/'+EQUALIZER_PRESET):
      self.preset = self.gconf.get_string(EQUALIZER_GCONF_PREFIX+'/'+EQUALIZER_PRESET)
    else:
      self.preset = "default"

    self.read_settings(self.preset)

  def reset_all(self):
    self.gconf.recursive_unset(EQUALIZER_GCONF_PREFIX, 0)	

    # Create default preset
    if not self.gconf.dir_exists(EQUALIZER_GCONF_PREFIX + '/default'):
      for i in range(0, 10):
        self.gconf.set_float(self.make_path(self.gconf_keys[i], 'default'), self.config[i])

    self.preset = "default"
    self.read_settings(self.preset)

  def read_settings(self, preset):
    for i in range(0,10):
      if preset == "default":
        self.config[i] = self.read_value(preset, self.gconf_keys[i], 0.0)
      else:
        self.config[i] = self.read_value(preset, self.gconf_keys[i], self.config[i])

  def apply_settings(self, eq):
    import sys
    if self.enabled:
      for i in range(0, 10):
        eq.set_property('band' + repr(i), self.config[i])
    else:
      for i in range(0, 10):
        eq.set_property('band' + repr(i), 0.0)

  def write_settings(self):
    preset = self.preset
    self.gconf.set_string(EQUALIZER_GCONF_PREFIX+'/'+EQUALIZER_PRESET, preset)
    self._write_enabled()
    for i in range(0, 10):
      self.gconf.set_float(self.make_path(self.gconf_keys[i], preset), self.config[i])

  def _write_enabled(self):
    self.gconf.set_bool(EQUALIZER_GCONF_PREFIX+'/'+EQUALIZER_ENABLED, self.enabled)

  def make_path(self, path, preset):
    return EQUALIZER_GCONF_PREFIX+'/' + preset + '/' + path

  def list_preset(self):
    return self.gconf.all_dirs(EQUALIZER_GCONF_PREFIX)

  def read_value(self, preset, value, default):
    gc = self.gconf
    path = self.make_path(value, preset)
    rv = gc.get_float(path)
    if(not rv):
      rv = default
      #gc.set_float(path, default)
    return rv

  def change_enabled(self, enabled, eq):
    self.enabled = enabled
    self.apply_settings(eq)
    self._write_enabled()

  def change_preset(self, new_preset, eq):
    if not new_preset:
      return

    self.preset = self.mangle(new_preset)

    if self.preset_exists(self.preset):
      self.read_settings(self.preset)
      self.apply_settings(eq)
    else:
      Gst.Preset.load_preset(eq, new_preset)
      self.write_settings()

  def preset_exists(self, preset):
    return self.gconf.dir_exists(self.mangle(EQUALIZER_GCONF_PREFIX + '/' + preset))

  def mangle(self, preset):
    #return preset
    return preset.replace(' ', '_')

  def demangle(self, preset):
    #return preset
    return preset.replace('_', ' ')
