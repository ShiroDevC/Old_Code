'''
Module for all views in this app.

The views contained in this app: Index view, Detail view,
Login view, Register view, User view, ChangeUser view,
ChangePassword view, logout view.

@author: Christian Breu <cbreu0@icloud.com>
'''

from django.shortcuts import render, get_object_or_404

from django.views import generic
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth import logout as log_out
from django.contrib import messages 

from django.db import IntegrityError
from .models import Entry, Comment

from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
    """
    View to display the blog entries with a pagination. The Paginator from 
    Django is used. 
    The context data that will be used for rendering the html template consist
    of the page object of the pagination an the username of the current logged
    in user. If the user object is not null the username is displayed in the template.
    """
    entry_list = Entry.objects.all()
    # using paginator to create a pagination for the entries
    paginator = Paginator(entry_list, 4) # Show 4 blog entries per page.
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user = request.user
    context = {'page_obj' : page_obj, 'username' : user.username}
    return render(request, 'blog/index.html', context)
    
class DetailView(generic.DetailView):
    """
    Generic view to display a given blog entry. The current logged in user is
    added to the context data for the html template. 
    """
    model = Entry
    template_name = 'blog/detail.html'
    
    
    def get_context_data(self, *, object_list=None, **kwargs):
        """ 
        This method override adds the "username" with the value of the current
        user to the context to be available in the template.
        """
        curr_user = self.request.user
        context = generic.DetailView.get_context_data(self, **kwargs)
        context["username"] = curr_user
        return context
    
    def post(self, request, pk, *args, **kwargs):
        """
        Custom post method for handling the post request from the create comment
        form in the detail.html. The comment data are retrieved from the request object
        and a new comment is created for the entry with the specified id(pk).
        In case the comment cannot be created, add an error message an redirect to
        the corresponding detail view. If the comment can be created without issue,
        redirect to the same detail view.
        """
        entry = get_object_or_404(Entry, pk=pk)
        try:
            time = timezone.localtime(timezone.now())
            com_text = request.POST['comment_text']
            com_auth = request.POST['comment_author']
            # create a new comment for the entry
            new_comment = entry.comment_set.create(comment_text=com_text, pub_date=time, author=com_auth)
            new_comment.comment_author = com_auth
            new_comment.pub_date = time
        except (KeyError, Comment.DoesNotExist):
            # Redisplay the question voting form and add error message
            return render(request, 'blog/detail.html', {
                'entry': entry,
                'error_message': "there was no comment",
            })
        else:
            # save comment to db and redirect to the same page to reload and show the new comment.
            new_comment.save()
            return HttpResponseRedirect(reverse('blog:detail', args=(pk,)))

class LoginView(generic.TemplateView):
    """
    View for the login functionality. This is a plain template view that will display
    a simple template with a form. The post method handles the submission of the form.
    """
    template_name = 'blog/login.html'
    
    
    def post(self, request, *args, **kwargs):
        """
        Method for handling a post request with login data from the user. If the
        username and the password can be authenticated with the database, the user
        will be logged in and redirected to the index view.
        If the password and username cannot be authenticated a message will be added
        that will be displayed in the html template to inform the user about the
        failed login.
        """
        username = request.POST['username']
        password = request.POST['password']
        
        #login with login function
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse('blog:index'))
        else:
            # Return an 'invalid login' error message.
            messages.error(request, "Login failed! Password or username not correct")
            return HttpResponseRedirect(reverse('blog:login'))

class RegisterView(generic.TemplateView):
    """
    This View manages the form to create a new user account. It simply displays
    a template with a form and handles the post request of the form in the post
    method.
    """
    template_name = 'blog/register.html'
     
    def post(self, request, *args, **kwargs):
        """
        this function will retrieve the user data for the new user account from the
        post data of the request. With these information a new user is created and
        information of the user will be set. The user will be saved to the database.
        If the account was created succesfully the user will be redirected to the login
        screen to login with the new account. 
        """ 
        try:
            username = request.POST['username']
            mail = request.POST['mail']
            password = request.POST['password']
            
            #create a user object with the given data
            user = User.objects.create_user(username, mail, password)
            
            #add the first and last name information to the newly created user
            user.first_name = request.POST['fname']
            user.last_name = request.POST['lname']
            user.save()
        except IntegrityError:
            # user already exists
            return render(request, 'blog/register.html', {
                'error_message': 'user already exists',
            })
        else:
            return HttpResponseRedirect(reverse('blog:login'))

class UserView(generic.TemplateView):
    """
    View for displaying the user information. In this view all user data(excluding the password can be seen).
    To display the user data the get context data method is overridden to include the 
    user object in the context. 
    """
    template_name = 'blog/user.html'
    
    
    def get_context_data(self, *, object_list=None, **kwargs):
        """ Method to add the currently logged in user to the context data for the html file.
        """
        curr_user = self.request.user
        context = generic.TemplateView.get_context_data(self, **kwargs)
        context["username"] = curr_user
        return context

class ChangeUserView(generic.TemplateView):
    """
    This view manages the screen for changing user details. The current user data
    are displayed, so they are added to the context data in the get context data 
    method.
    """
    template_name = 'blog/userchange.html'
    
    def get_context_data(self, *, object_list=None, **kwargs):
        """ Method to add the currently logged in user to the context data for the html file.
        """
        curr_user = self.request.user
        context = generic.TemplateView.get_context_data(self, **kwargs)
        context["username"] = curr_user
        return context
    
    def post(self, request, *args, **kwargs):
        """
        this function will retrieve the changed user data for the from the post
        data of the request. With these data the user is updated and saved to the database.
        If the change was succesfull the user will be redirected to the user view.
        """ 
        try:
            user = request.user
            if user is not None:
                user.username = request.POST['username']
                user.mail = request.POST['mail']
                user.first_name = request.POST['fname']
                user.last_name = request.POST['lname']
                user.save()
            else:
                messages.error(request, "retrieving user failed!")
                
        except IntegrityError:
            # user already exists
            return render(request, 'blog/userchange.html', {
                'error_message': 'user name already exists',
            })
        else:
            return HttpResponseRedirect(reverse('blog:user'))
    
class ChangePasswordView(generic.TemplateView):
    """
    This view manages the screen for changing the password. The post request will
    be handled in the post method.
    """
    template_name = 'blog/passwordchange.html'
    
    def get_context_data(self, *, object_list=None, **kwargs):
        """ Method to add the currently logged in user to the context data for the html file.
        """
        curr_user = self.request.user
        context = generic.TemplateView.get_context_data(self, **kwargs)
        context["username"] = curr_user
        return context
    
    def post(self, request, *args, **kwargs):
        """
        this function will retrieve the old and new password from the post
        data of the request. If the old password is correct the password will be
        changed and saved to the database.If the change was succesfull the user
        will be redirected to the user view.
        """ 
        try:
            # check if the old password is correct.
            user = authenticate(request, username=request.user.username, password= request.POST['oldpassword'])    
            if user is not None:
                #change password to new one.
                user.set_password(request.POST['password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.info(request, "your password was succesfully changed!")
            else:
                messages.error(request, "The old password is not correct.")
                return HttpResponseRedirect(reverse('blog:passwordchange')) 
        except IntegrityError:
            # user already exists
            return render(request, 'blog/passwordchange.html', {
                'error_message': 'password already exists',
            })
        else:
            return HttpResponseRedirect(reverse('blog:user'))    
    
    
def logout(request):
    """
    View to log the current user out and go back to the login screen.
    """
    # logs the current user out.
    log_out(request)
    return HttpResponseRedirect(reverse('blog:login'))


    
    
    
    
    
    
    
    
    
