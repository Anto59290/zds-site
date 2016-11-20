# coding: utf-8

import os
import shutil

from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import Group
from hashlib import md5

from zds.forum.factories import CategoryFactory, ForumFactory, TopicFactory, PostFactory
from zds.notification.models import TopicAnswerSubscription
from zds.member.factories import ProfileFactory, StaffProfileFactory
from zds.member.models import TokenForgotPassword, TokenRegister, Profile
from zds.tutorialv2.factories import PublishableContentFactory, PublishedContentFactory
from zds.gallery.factories import GalleryFactory, ImageFactory
from zds.utils.models import Alert
from zds.settings import BASE_DIR


overrided_zds_app = settings.ZDS_APP
overrided_zds_app['content']['repo_private_path'] = os.path.join(BASE_DIR, 'contents-private-test')
overrided_zds_app['content']['repo_public_path'] = os.path.join(BASE_DIR, 'contents-public-test')


@override_settings(MEDIA_ROOT=os.path.join(BASE_DIR, 'media-test'))
@override_settings(ZDS_APP=overrided_zds_app)
class MemberModelsTest(TestCase):

    def setUp(self):
        self.user1 = ProfileFactory()
        self.staff = StaffProfileFactory()

        # Create a forum for later test
        self.forumcat = CategoryFactory()
        self.forum = ForumFactory(category=self.forumcat)
        self.forumtopic = TopicFactory(forum=self.forum, author=self.staff.user)

    def test_unicode_of_username(self):
        self.assertEqual(self.user1.__unicode__(), self.user1.user.username)

    def test_get_absolute_url_for_details_of_member(self):
        self.assertEqual(self.user1.get_absolute_url(), '/membres/voir/{0}/'.format(self.user1.user.username))

    def test_get_avatar_url(self):
        # if no url was specified -> gravatar !
        self.assertEqual(self.user1.get_avatar_url(),
                         'https://secure.gravatar.com/avatar/{0}?d=identicon'.
                         format(md5(self.user1.user.email.lower()).hexdigest()))
        # if an url is specified -> take it !
        user2 = ProfileFactory()
        testurl = 'http://test.com/avatar.jpg'
        user2.avatar_url = testurl
        self.assertEqual(user2.get_avatar_url(), testurl)

        # if url is relative, send absolute url
        gallerie_avtar = GalleryFactory()
        image_avatar = ImageFactory(gallery=gallerie_avtar)
        user2.avatar_url = image_avatar.physical.url
        self.assertNotEqual(user2.get_avatar_url(), image_avatar.physical.url)
        self.assertIn("http", user2.get_avatar_url())

    def test_get_post_count(self):
        # Start with 0
        self.assertEqual(self.user1.get_post_count(), 0)
        # Post !
        PostFactory(topic=self.forumtopic, author=self.user1.user, position=1)
        # Should be 1
        self.assertEqual(self.user1.get_post_count(), 1)

    def test_get_topic_count(self):
        # Start with 0
        self.assertEqual(self.user1.get_topic_count(), 0)
        # Create Topic !
        TopicFactory(forum=self.forum, author=self.user1.user)
        # Should be 1
        self.assertEqual(self.user1.get_topic_count(), 1)

    def test_get_tuto_count(self):
        # Start with 0
        self.assertEqual(self.user1.get_tuto_count(), 0)
        # Create Tuto !
        minituto = PublishableContentFactory(type='TUTORIAL')
        minituto.authors.add(self.user1.user)
        minituto.gallery = GalleryFactory()
        minituto.save()
        # Should be 1
        self.assertEqual(self.user1.get_tuto_count(), 1)

    def test_get_tutos(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_tutos()), 0)
        # Create Tuto !
        minituto = PublishableContentFactory(type='TUTORIAL')
        minituto.authors.add(self.user1.user)
        minituto.gallery = GalleryFactory()
        minituto.save()
        # Should be 1
        tutos = self.user1.get_tutos()
        self.assertEqual(len(tutos), 1)
        self.assertEqual(minituto, tutos[0])

    def test_get_draft_tutos(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_draft_tutos()), 0)
        # Create Tuto !
        drafttuto = PublishableContentFactory(type='TUTORIAL')
        drafttuto.authors.add(self.user1.user)
        drafttuto.gallery = GalleryFactory()
        drafttuto.save()
        # Should be 1
        drafttutos = self.user1.get_draft_tutos()
        self.assertEqual(len(drafttutos), 1)
        self.assertEqual(drafttuto, drafttutos[0])

    def test_get_public_tutos(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_public_tutos()), 0)
        # Create Tuto !
        publictuto = PublishableContentFactory(type='TUTORIAL')
        publictuto.authors.add(self.user1.user)
        publictuto.gallery = GalleryFactory()
        publictuto.sha_public = "whatever"
        publictuto.save()
        # Should be 0 because publication was not used
        publictutos = self.user1.get_public_tutos()
        self.assertEqual(len(publictutos), 0)
        PublishedContentFactory(author_list=[self.user1.user])
        self.assertEqual(len(self.user1.get_public_tutos()), 1)

    def test_get_validate_tutos(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_validate_tutos()), 0)
        # Create Tuto !
        validatetuto = PublishableContentFactory(type='TUTORIAL', author_list=[self.user1.user])
        validatetuto.sha_validation = 'whatever'
        validatetuto.save()
        # Should be 1
        validatetutos = self.user1.get_validate_tutos()
        self.assertEqual(len(validatetutos), 1)
        self.assertEqual(validatetuto, validatetutos[0])

    def test_get_beta_tutos(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_beta_tutos()), 0)
        # Create Tuto !
        betatetuto = PublishableContentFactory(type='TUTORIAL')
        betatetuto.authors.add(self.user1.user)
        betatetuto.gallery = GalleryFactory()
        betatetuto.sha_beta = 'whatever'
        betatetuto.save()
        # Should be 1
        betatetutos = self.user1.get_beta_tutos()
        self.assertEqual(len(betatetutos), 1)
        self.assertEqual(betatetuto, betatetutos[0])

    def test_get_article_count(self):
        # Start with 0
        self.assertEqual(self.user1.get_tuto_count(), 0)
        # Create article !
        minituto = PublishableContentFactory(type='ARTICLE')
        minituto.authors.add(self.user1.user)
        minituto.gallery = GalleryFactory()
        minituto.save()
        # Should be 1
        self.assertEqual(self.user1.get_article_count(), 1)

    def test_get_articles(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_articles()), 0)
        # Create article !
        article = PublishableContentFactory(type='ARTICLE')
        article.authors.add(self.user1.user)
        article.save()
        # Should be 1
        articles = self.user1.get_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(article, articles[0])

    def test_get_public_articles(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_public_articles()), 0)
        # Create article !
        article = PublishableContentFactory(type='ARTICLE')
        article.authors.add(self.user1.user)
        article.sha_public = 'whatever'
        article.save()
        # Should be 0
        articles = self.user1.get_public_articles()
        self.assertEqual(len(articles), 0)
        # Should be 1
        PublishedContentFactory(author_list=[self.user1.user], type="Article")
        self.assertEqual(len(self.user1.get_public_tutos()), 1)

    def test_get_validate_articles(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_validate_articles()), 0)
        # Create article !
        article = PublishableContentFactory(type='ARTICLE')
        article.authors.add(self.user1.user)
        article.sha_validation = 'whatever'
        article.save()
        # Should be 1
        articles = self.user1.get_validate_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(article, articles[0])

    def test_get_draft_articles(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_draft_articles()), 0)
        # Create article !
        article = PublishableContentFactory(type='ARTICLE')
        article.authors.add(self.user1.user)
        article.save()
        # Should be 1
        articles = self.user1.get_draft_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(article, articles[0])

    def test_get_beta_articles(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_beta_articles()), 0)
        # Create article !
        article = PublishableContentFactory(type='ARTICLE')
        article.authors.add(self.user1.user)
        article.sha_beta = 'whatever'
        article.save()
        # Should be 1
        articles = self.user1.get_beta_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(article, articles[0])

    def test_get_posts(self):
        # Start with 0
        self.assertEqual(len(self.user1.get_posts()), 0)
        # Post !
        apost = PostFactory(topic=self.forumtopic, author=self.user1.user, position=1)
        # Should be 1
        posts = self.user1.get_posts()
        self.assertEqual(len(posts), 1)
        self.assertEqual(apost, posts[0])

    def test_get_invisible_posts_count(self):
        # Start with 0
        self.assertEqual(self.user1.get_invisible_posts_count(), 0)
        # Post !
        PostFactory(topic=self.forumtopic, author=self.user1.user, position=1, is_visible=False)
        # Should be 1
        self.assertEqual(self.user1.get_invisible_posts_count(), 1)

    def test_get_alerts_posts_count(self):
        # Start with 0
        self.assertEqual(self.user1.get_alerts_posts_count(), 0)
        # Post and Alert it !
        post = PostFactory(topic=self.forumtopic, author=self.user1.user, position=1)
        Alert.objects.create(author=self.user1.user, comment=post, scope='FORUM', pubdate=datetime.now())
        # Should be 1
        self.assertEqual(self.user1.get_alerts_posts_count(), 1)

    def test_can_read_now(self):
        self.user1.user.is_active = False
        self.assertFalse(self.user1.can_write_now())
        self.user1.user.is_active = True
        self.assertTrue(self.user1.can_write_now())
        profile_ban_temp = ProfileFactory()
        profile_ban_temp.can_read = False
        profile_ban_temp.can_write = False
        profile_ban_temp.end_ban_read = datetime.now() + timedelta(days=1)
        profile_ban_temp.save()
        self.assertFalse(profile_ban_temp.can_read_now())
        profile_ls_temp = ProfileFactory()
        profile_ls_temp.can_write = False
        profile_ls_temp.end_ban_write = datetime.now() + timedelta(days=1)
        profile_ls_temp.save()
        self.assertTrue(profile_ls_temp.can_read_now())

    def test_can_write_now(self):
        self.user1.user.is_active = False
        self.assertFalse(self.user1.can_write_now())
        self.user1.user.is_active = True
        self.assertTrue(self.user1.can_write_now())
        profile_ban_temp = ProfileFactory()
        profile_ban_temp.can_read = False
        profile_ban_temp.can_write = False
        profile_ban_temp.end_ban_read = datetime.now() + timedelta(days=1)
        profile_ban_temp.save()
        self.assertFalse(profile_ban_temp.can_write_now())
        profile_ls_temp = ProfileFactory()
        profile_ls_temp.can_write = False
        profile_ls_temp.end_ban_write = datetime.now() + timedelta(days=1)
        profile_ls_temp.save()
        self.assertFalse(profile_ls_temp.can_write_now())

    def test_get_followed_topics(self):
        # Start with 0
        self.assertEqual(len(TopicAnswerSubscription.objects.get_objects_followed_by(self.user1.user)), 0)
        # Follow !
        TopicAnswerSubscription.objects.toggle_follow(self.forumtopic, self.user1.user)
        # Should be 1
        topicsfollowed = TopicAnswerSubscription.objects.get_objects_followed_by(self.user1.user)
        self.assertEqual(len(topicsfollowed), 1)
        self.assertEqual(self.forumtopic, topicsfollowed[0])

    def test_get_city_with_wrong_ip(self):
        # Set a local IP to the user
        self.user1.last_ip_address = '127.0.0.1'
        # Then the get_city is not found and return empty string
        self.assertEqual('', self.user1.get_city())

        # Same goes for IPV6
        # Set a local IP to the user
        self.user1.last_ip_address = '0000:0000:0000:0000:0000:0000:0000:0001'
        # Then the get_city is not found and return empty string
        self.assertEqual('', self.user1.get_city())

    def test_reachable_manager(self):
        # profile types
        profile_normal = ProfileFactory()
        profile_superuser = ProfileFactory()
        profile_superuser.user.is_superuser = True
        profile_superuser.user.save()
        profile_inactive = ProfileFactory()
        profile_inactive.user.is_active = False
        profile_inactive.user.save()
        profile_bot = ProfileFactory()
        profile_bot.user.username = settings.ZDS_APP["member"]["bot_account"]
        profile_bot.user.save()
        profile_anonymous = ProfileFactory()
        profile_anonymous.user.username = settings.ZDS_APP["member"]["anonymous_account"]
        profile_anonymous.user.save()
        profile_external = ProfileFactory()
        profile_external.user.username = settings.ZDS_APP["member"]["external_account"]
        profile_external.user.save()
        profile_ban_def = ProfileFactory()
        profile_ban_def.can_read = False
        profile_ban_def.can_write = False
        profile_ban_def.save()
        profile_ban_temp = ProfileFactory()
        profile_ban_temp.can_read = False
        profile_ban_temp.can_write = False
        profile_ban_temp.end_ban_read = datetime.now() + timedelta(days=1)
        profile_ban_temp.save()
        profile_unban = ProfileFactory()
        profile_unban.can_read = False
        profile_unban.can_write = False
        profile_unban.end_ban_read = datetime.now() - timedelta(days=1)
        profile_unban.save()
        profile_ls_def = ProfileFactory()
        profile_ls_def.can_write = False
        profile_ls_def.save()
        profile_ls_temp = ProfileFactory()
        profile_ls_temp.can_write = False
        profile_ls_temp.end_ban_write = datetime.now() + timedelta(days=1)
        profile_ls_temp.save()

        # groups

        bot = Group(name=settings.ZDS_APP["member"]["bot_group"])
        bot.save()

        # associate account to groups
        bot.user_set.add(profile_anonymous.user)
        bot.user_set.add(profile_external.user)
        bot.user_set.add(profile_bot.user)
        bot.save()

        # test reachable user
        profiles_reacheable = Profile.objects.contactable_members().all()
        self.assertIn(profile_normal, profiles_reacheable)
        self.assertIn(profile_superuser, profiles_reacheable)
        self.assertNotIn(profile_inactive, profiles_reacheable)
        self.assertNotIn(profile_anonymous, profiles_reacheable)
        self.assertNotIn(profile_external, profiles_reacheable)
        self.assertNotIn(profile_bot, profiles_reacheable)
        self.assertIn(profile_unban, profiles_reacheable)
        self.assertNotIn(profile_ban_def, profiles_reacheable)
        self.assertNotIn(profile_ban_temp, profiles_reacheable)
        self.assertIn(profile_ls_def, profiles_reacheable)
        self.assertIn(profile_ls_temp, profiles_reacheable)

    def tearDown(self):
        if os.path.isdir(settings.ZDS_APP['content']['repo_private_path']):
            shutil.rmtree(settings.ZDS_APP['content']['repo_private_path'])
        if os.path.isdir(settings.ZDS_APP['content']['repo_public_path']):
            shutil.rmtree(settings.ZDS_APP['content']['repo_public_path'])
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)


class TestTokenForgotPassword(TestCase):

    def setUp(self):
        self.user1 = ProfileFactory()
        self.token = TokenForgotPassword.objects.create(user=self.user1.user,
                                                        token="abcde",
                                                        date_end=datetime.now())

    def test_get_absolute_url(self):
        self.assertEqual(self.token.get_absolute_url(), '/membres/new_password/?token={0}'.format(self.token.token))


class TestTokenRegister(TestCase):

    def setUp(self):
        self.user1 = ProfileFactory()
        self.token = TokenRegister.objects.create(user=self.user1.user,
                                                  token="abcde",
                                                  date_end=datetime.now())

    def test_get_absolute_url(self):
        self.assertEqual(self.token.get_absolute_url(), '/membres/activation/?token={0}'.format(self.token.token))

    def test_unicode(self):
        self.assertEqual(self.token.__unicode__(), '{0} - {1}'.format(self.user1.user.username, self.token.date_end))
