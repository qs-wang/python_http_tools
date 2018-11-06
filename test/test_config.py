import unittest
from os.path import expanduser

class TestConfigFunctions(unittest.TestCase):
    def test_create_config(self):
        from src.config import create_config
        home = expanduser('~')
        config_file = create_config(home + '/.flam/config')
        self.assertIsNotNone(config_file)

    def test_load_config(self):
        from src.config import parse_config
        home = expanduser('~')
        config = parse_config(home + '/.flam/config')
        self.assertEqual(config,{})
        
    # def test_save_config(self):
    #     import utils
    #     home = expanduser('~')
    #     config = utils.get_config(home + '/.flam/config')

    #     self.assertIsNotNone(config)
    #     config.set('DEFAULT', 'token', '12345')
    #     utils.write_config(home + '/.flam/config', config)
        
    #     newconfig = utils.get_config(home + '/.flam/config')
    #     token = newconfig.get('DEFAULT', 'token')
    #     self.assertEqual(token, '12345')

    #     config.set('DEFAULT', 'user', 'user1')
    #     with self.assertRaises(AttributeError):
    #         utils.write_config(home + '/.flam/config',None)
            
        


