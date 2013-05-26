from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/service/%d' % self.pk


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    skillsTeach = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)

    skillsLearn = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)
    servicesOffered = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)
    servicesWanted = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)

    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    phone = models.CharField(max_length=11)

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        try:
            existing = UserProfile.objects.get(user=self.user)
            self.id = existing.id #force update instead of insert
        except UserProfile.DoesNotExist:
            pass 
        models.Model.save(self, *args, **kwargs)

    def decode(self, field):
        pks = []
        if not field or hasattr(field, 'real'):
            return []
        for pk in field.split(','):
            if pk:
                pks.append(int(pk))
        return pks

    def addPK(self, field, pk):
        content = getattr(self, field)
        if not content:
            setattr(self, field, pk)
        else:
            setattr(self, field, content + ',' + str(pk))
        self.save()

    def getObjects(self, objects):
        pks = self.decode(objects)
        skills = []
        for pk in pks:
            try:
                skill = Service.objects.get(pk=pk)
                skills.append(skill)
            except Service.DoesNotExist:
                pass
        return skills

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

