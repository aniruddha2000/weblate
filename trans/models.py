from django.db import models
from django.conf import settings
from lang.models import Language
import os
import os.path

PLURAL_SEPARATOR = '\x00\x00'

class Project(models.Model):
    name = models.CharField(max_length = 100)
    slug = models.SlugField(db_index = True)
    web = models.URLField()
    mail = models.EmailField()
    instructions = models.URLField()

    @models.permalink
    def get_absolute_url(self):
        return ('trans.views.show_project', (), {'project': self.slug})

    def get_path(self):
        return os.path.join(settings.GIT_ROOT, self.slug)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Create filesystem directory for storing data
        p = self.get_path()
        if not os.path.exists(p):
            os.makedirs(p)
        super(Project, self).save(*args, **kwargs)

class SubProject(models.Model):
    name = models.CharField(max_length = 100)
    slug = models.SlugField(db_index = True)
    project = models.ForeignKey(Project)
    repo = models.CharField(max_length = 200)
    branch = models.CharField(max_length = 50)
    filemask = models.CharField(max_length = 200)
    style_choices = (('po', 'GNU Gettext'), ('ts', 'Qt TS'))
    style = models.CharField(max_length = 10, choices = style_choices)

    @models.permalink
    def get_absolute_url(self):
         return ('trans.views.show_subproject', (), {'project': self.project.slug, 'subproject': self.slug})

    def __unicode__(self):
        return '%s/%s' (self.project.__unicode__(), self.name)

class Translation(models.Model):
    subproject = models.ForeignKey(SubProject)
    language = models.ForeignKey(Language)
    translated = models.FloatField()
    fuzzy = models.FloatField()
    revision = models.CharField(max_length = 40)
    filename = models.CharField(max_length = 200)

    @models.permalink
    def get_absolute_url(self):
         return ('trans.views.show_translation', (), {'project': self.subproject.slug, 'subproject': self.subproject.slug, 'lang': self.language.code})

    def __unicode__(self):
        return '%s@%s' (self.language.name, self.subproject.__unicode__())

class Unit(models.Model):
    translation = models.ForeignKey(Translation)
    location = models.TextField()
    flags = models.TextField()
    source = models.TextField()
    target = models.TextField()

    def is_plural(self):
        return self.source.find(PLURAL_SEPARATOR) != -1

    def get_source_plurals(self):
        return self.source.split(PLURAL_SEPARATOR)

    def get_target_plurals(self):
        ret = self.target.split(PLURAL_SEPARATOR)
        plurals = self.translation.language.nplurals
        if len(ret) == plurals:
            return ret

        while len(ret) < plurals:
            ret.append('')

        while len(ret) > plurals:
            del(ret[-1])

        return ret
