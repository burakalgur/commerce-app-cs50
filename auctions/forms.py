from django import forms
from .models import Auction, Category

class CreateListingForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Auction
        fields = ('name', 'description', 'price', 'photo', 'category')
        
class BidForm(forms.Form):
    offer = forms.FloatField()
    
class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

