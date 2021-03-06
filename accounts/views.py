import datetime
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from accounts.forms import UserRegistrationForm, UserLoginForm
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():

            try:
                customer = stripe.Charge.create(
                    amount = 499,
                    currency = "USD",
                    description = form.cleaned_data['email'],
                    card = form.cleaned_data['stripe_id'],
                )
            except stripe.error.CardError, e:
                messages.error(request, "Your card was declined!")

            if customer.paid:
                form.save()

                user = auth.authenticate(email=request.POST.get('email'),
                                         password=request.POST.get('password1'))

                if user:
                    auth.login(request, user)
                    messages.success(request, "You have successfully registered")
                    return redirect(reverse('profile'))

                else:
                    messages.error(request, "unable to log you in at this time!")
            else:
                messages.error(request, "We wer unable to take a payment with that card!")
    else:
        today = datetime.date.today()
        form = UserRegistrationForm(initial={'expiry_month': today.month,
                                             'expiry_year': today.year})

    args = {'form':form, 'publishable' : settings.STRIPE_PUBLISHABLE}
    args.update(csrf(request))

    return render(request, 'register.html', args)



def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(email=request.POST.get('email'),
                                    password=request.POST.get('password'))

            if user is not None:
                auth.login(request, user)
                messages.error(request, "You have successfully logged in")
                return redirect(reverse('profile'))
            else:
                form.add_error(None, "Your email or password was not recognised")

    else:
        form = UserLoginForm()

    args = {'form':form}
    args.update(csrf(request))
    return render(request, 'login.html', args)

@login_required(login_url='/accounts/login/')
def profile(request):
    return render(request, 'profile.html')

def logout(request):
    auth.logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect(reverse('index'))