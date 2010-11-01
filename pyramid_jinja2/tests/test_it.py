## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import unittest

class Base(object):
    def setUp(self):
        from pyramid.configuration import Configurator
        self.config = Configurator()
        self.config.begin()
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'templates')

    def tearDown(self):
        self.config.end()

class Test_renderer_factory(Base, unittest.TestCase):
    def _callFUT(self, info):
        from pyramid_jinja2 import renderer_factory
        return renderer_factory(info)

    def test_no_directories(self):
        from pyramid.exceptions import ConfigurationError
        info = {'name':'helloworld.jinja2', 'package':None,
                'registry':self.config.registry, 'settings':None}
        self.assertRaises(ConfigurationError, self._callFUT, info)

    def test_no_environment(self):
        from pyramid_jinja2 import IJinja2Environment
        settings = {'jinja2.directories':self.templates_dir}
        info = {'name':'helloworld.jinja2', 'package':None,
                'registry':self.config.registry, 'settings':settings}
        renderer = self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.loader.searchpath, [self.templates_dir])
        self.assertEqual(renderer.info, info)
        self.assertEqual(renderer.environment, environ)

    def test_composite_directories_path(self):
        from pyramid_jinja2 import IJinja2Environment
        twice = self.templates_dir + '\n' + self.templates_dir
        settings = {'jinja2.directories':twice}
        info = {'name':'helloworld.jinja2', 'package':None,
                'registry':self.config.registry, 'settings':settings}
        self._callFUT(info)
        environ = self.config.registry.getUtility(IJinja2Environment)
        self.assertEqual(environ.loader.searchpath, [self.templates_dir]*2)

    def test_with_environ(self):
        from pyramid_jinja2 import IJinja2Environment
        environ = dict()
        self.config.registry.registerUtility(environ, IJinja2Environment)
        info = {'name':'helloworld.jinja2', 'package':None,
                'registry':self.config.registry, 'settings':{}}
        renderer = self._callFUT(info)
        self.assertEqual(renderer.environment, environ)
        self.assertEqual(renderer.info, info)

class Jinja2TemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_jinja2 import Jinja2TemplateRenderer
        return Jinja2TemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITemplateRenderer
        verifyObject(ITemplateRenderer, self._makeOne(None, None))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        environ = DummyEnvironment()
        info = {'name':'name'}
        instance = self._makeOne(info, environ)
        result = instance({}, {'system':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')

    def test_call_with_system_context(self):
        # lame
        environ = DummyEnvironment()
        info = {'name':'name'}
        instance = self._makeOne(info, environ)
        result = instance({}, {'context':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')
        self.assertEqual(environ.values, {'context':1})

    def test_implementation(self):
        environ = DummyEnvironment()
        info = {'name':'name'}
        instance = self._makeOne(info, environ)
        result = instance.implementation().render({})
        self.assertEqual(result, u'result')
        
class TestIntegration(unittest.TestCase):
    def setUp(self):
        import pyramid_jinja2
        from pyramid.configuration import Configurator
        self.config = Configurator()
        self.config.begin()
        self.config.add_settings({'jinja2.directories':
                                  'pyramid_jinja2.tests:templates'})
        self.config.add_renderer('.jinja2',
                                 pyramid_jinja2.renderer_factory)

    def tearDown(self):
        self.config.end()

    def test_render(self):
        from pyramid.renderers import render
        result = render('helloworld.jinja2', {'a':1})
        self.assertEqual(result, u'\nHello föö')

class DummyEnvironment(object):
    def get_template(self, path):
        self.path = path
        return self

    def render(self, values):
        self.values = values
        return u'result'
        
