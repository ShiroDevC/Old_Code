'''
Module for test.

There are tests for the Index view and the
Details view.

@author: Christian Breu <cbreu0@icloud.com>
'''

from django.test import TestCase

from django.urls import reverse
from django.utils import timezone

from .models import Entry

import tempfile


# helper functions

def create_blog_entry(title, text, pub_d, auth):
    """
    helper function to create a blog entry with the given title, text, pub_date
    and author. 
    There is no functionality to add a picture to the entry at the moment.
    """
    return Entry.objects.create(entry_title = title, entry_text = text, pub_date = pub_d, author = auth)

def add_image(entr, image):
    """
    Helper function that creates a choice and adds it to the choice_set of the given question.
    """
    entr.imagem_set.create(picture = image)
    
def add_comment(entry, com_text, com_auth, com_time):
    """
    This helper function creates a comment and adds it to the given entry.
    """
    entry.comment_set.create(comment_text = com_text, author = com_auth, pub_date = com_time)

# actual test functions

class IndexViewTest(TestCase):
    """
    This class contains tests for the index view.
    """    
    
    def test_no_entry(self):
        """
        This function tests the display of the entries if there are no entries.
        If no questions exist, an appropriate message shall be displayed.
        """
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No entries are available.")
        self.assertQuerysetEqual(response.context['page_obj'], [])
        
    def test_pagination(self):
        """
        Test the pagination of a set of entries. The entries should be split up in two pages
        because the pagination only shows up to 4 entries per page, so the 5th entry shall not
        be contained in the first page, which is received 
        """
        time = timezone.localtime(timezone.now())
        create_blog_entry(title="test", text="test text", pub_d=time, auth="test author")
        create_blog_entry(title="test2", text="test text2", pub_d=time, auth="test author2")
        create_blog_entry(title="test3", text="test text3", pub_d=time, auth="test author3")
        curr_page_entry = create_blog_entry(title="test4", text="test text4", pub_d=time, auth="test author4")
        next_page_entry = create_blog_entry(title="test5", text="test text5 ", pub_d=time, auth="test author5")
        response = self.client.get(reverse('blog:index'))
        self.assertNotContains(response, next_page_entry.entry_title )
        self.assertContains(response, curr_page_entry.entry_title )
    
class DetailsViewTest(TestCase):
    """
    This class contains tests for the Details view.
    The entry properties are tested if the correct content is displayed
    on the page. The tested properties are title, text, author, comments
    and images. 
    For the publication date there is an unsolved problem regarding timezones.
    """
    
    def test_image_entry(self):
        """
        Test to check whether the images are working from the entry model. 
        For the test a temporary file is created to make the test faster and to no create
        any image overhead.
        Note: there is an option to use real image(commented out)
        """
        time = timezone.localtime(timezone.now())
        entry1 = create_blog_entry(title="testimage", text="test text", pub_d=time,
                                        auth="test author", )
        
        
        t_image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        
        #This option would use a real picture and upload it.
        #test_image = SimpleUploadedFile(name='christianbreu1015.jpg', content=open('media/photos/entry/christianbreu1015.jpg', 'rb').read(), content_type='image/jpeg')
        
        add_image(entry1, t_image)
        url = reverse('blog:detail', args=(entry1.id,))
        response = self.client.get(url)
        self.assertContains(response, t_image )

    def test_complete_entry(self):
        """
        This test checks if all entry data are as expected. The tested data
        are entry title, entry text and entry author.
        """
        time = timezone.localtime(timezone.now())
        test_entry = create_blog_entry(title="test entry", text="test text", pub_d=time, auth="test author")
        url = reverse('blog:detail', args=(test_entry.id,))
        response = self.client.get(url)
        self.assertContains(response, test_entry.entry_title)
        self.assertContains(response, test_entry.entry_text)
        
        #There is a problem with the timezone.now and datefield compatibility.
        #Because of this problem the test cannot be done for time...
        #self.assertContains(response, time)
        self.assertContains(response, test_entry.author)
        
    def test_comments(self):
        """
        This test checks whether comments can be added and can be found in the
        corresponding detail view.
        """
        time = timezone.localtime(timezone.now())
        test_entry = create_blog_entry(title="test entry", text="test text", pub_d=time, auth="test author")
        add_comment(test_entry, "test comment 1", "Peter North", time)
        add_comment(test_entry, "test comment 2", "samuel koch", time)
        url = reverse('blog:detail', args=(test_entry.id,))
        response = self.client.get(url)
        self.assertContains(response, "test comment 1")
        self.assertContains(response, "samuel koch")
        
    
    
    
    
       
    
