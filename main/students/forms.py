from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from django import forms
from django.contrib.auth.models import User

from .models import Student, PostAnAd

from django.core.exceptions import ValidationError


from django.core.files.images import get_image_dimensions

class StudentSignupForm (UserCreationForm):
    age = forms.IntegerField()
    city = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone=forms.CharField(max_length=11)
    class Meta:
        model = User
        fields = ['username',"email","first_name","last_name",'age', 'city','phone' , "password1", 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Account with that email already exists")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) < 11 or phone.isdigit() != True:
            raise ValidationError("Phone Number must be of 11 digits")
        return phone


class StudentProfile (ModelForm):
    class Meta:
        model = Student
        fields = "__all__"
        exclude = ['student', "email", "username"]




class PostAnAdForm (forms.Form):
    SUBJECT = (
        ("Mathematics", "mathematics"),
        ("English", "english"),
        ("Physics", "physics"),
        ("Science", "science"),
        ("Chemistry", "chemistry"),
        ("Biology", "biology"),
        ("Economics", "economics"),
        ("Accounts", "accounts"),
        ("Quran", "quran"),
        ("Financial Accounting", "financial accounting"),
        ("Financial Management", "financial management"),
        ("CIMA" , "cima"),
        ("Cost Accounting", "cost accounting"),
        ("Zoology", "zoology"),
        ("ACCA", "acca"),
        ("GRE", "gre"),
        ("GMAT", "gmat"),
        ("SAT", "sat"),
        ("TOEFL", "toefl"),
        ("Agriculture", "agriculture"),
        ("Arabic", "arabic"),
        ("Art and Design", "art and design"),
        ("Business Studies", "business studies"),
        ("Design and Communication", 'design and communication'),
        ("Commerce", "Commerce"),
        ("Commercial Studies", "commercial studies"),
        ("Computer Science", "computer science"),
        ("Design and Technology", "design and technology"),
        ("Environmental Management", "environmental management"),
        ("Fashion and Textile", "fashion and textile"),
        ("Food and Nutrition", "food and nutrition"),
        ("French", "french"),
        ("Geography", "geography"),
        ("History", "history") ,
        ("Islamiyat", "islamiyat"),
        ("English literature", "english literature"),
        ("Paksitan Studies", "paksitan studies"),
        ("Sociology", "sociology"),
        ("Statistics", "statistics"),
        ("Turkish Language", "turkish language"),
        ("German Language", "german language"),
        ("Mandarin (Chinese) Language", "mandarin (chinese) language"),
        ("Spanish Language", "spanish language"),
        ("Programming", "programming"),
        ("Informational Technology", "informational technology"),
        ("Media Studies", "media studies"),
        ("Marketing", "marketing"),
        ("Management", "management"),
        ("Psycology", "psycology"),
        ("Law", "Law"),
        ("Business Law", "business law"),
        ("Corporate Law", "corporate law"),
        ("CFA", "cfa"),
        ("Corporate Finance", "corporate finance"),
        ("Actuarial Science", "actuarial science"),
        ("Human Resource (HR)", "human resource (HR)"),
        ("ECAT Entry Test", "CAT tntry test"),
        ("MCAT Entry Test", "MCAT entry test"),
        ("LSAT", "lsat"),
        ("Econometric", "econometric"),
        ("Public Finance", "public finance"),
        ("Tax", "tax"),
        ("Audit", "audit"),
        ("Financial Management", "financial management"),
        ("Regression Analysis", "regression analysis"),
        ("Quantitative Finance", "quantitative finance"),
        ("Finance", "Finance"),
        ("Business Finance", "business finance"),
        ("Additional Mathematics", "additional mathematics"),
        ("Social Studies", "social studies"),
        ("Digital Marketing", "digital marketing"),
        ("Art", "art"),
        ("Painting", "painting"),
        ("Data Science", "Data Science"),
        ("Microsoft Excel", "microsoft excel"),
        ("Microsoft Word", "microsoft word"),
        ("Microsoft PowerPoint", "microsoft powerpoint"),
        ("Microsoft Office", "microsoft office"),
        ("Primary (all subjects)", "primary (all subjects)"),
        ("Secondary (all subjects)", "secondary (all subjects)"),
        ("IELTS", "ielts"),
        ("English Drafting", "English Drafting"),
        ("IBA test preparation", "IBA test preparation"),
        ("Bio-Technology", "bio-technology"),
        ("Home Economics", "home economics"),
        ("Computer Lab Instructor", "computer lab instructor"),
    )


    TUITIONLEVEL = (
        ("Primary (class 1-5)", "Primary (class 1-5)"),
        ("Matric", "Matric"),
        ("University", "University"),
        ("Professional", "Professional"),
        ("Secondary (class 6-8)", "Secondary (class 6-8)"),
        ("Intermediate", "Intermediate"),
        ("O Level", "O Level"),
        ("A Level", "A Level"),
        ("SAT-I / SAT-II / E-CAT / M-CAT / GRE / GMAT / Entry test", "SAT-I / SAT-II / E-CAT / M-CAT / GRE / GMAT / Entry test"),
        ("IELTS / TOEFL", "IELTS / TOEFL"),
        ("Quran / Religious Studies", "Quran / Religious Studies"),

    )

    subject = forms.ChoiceField(
        choices=SUBJECT,
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    tuition_level = forms.ChoiceField(
        choices=TUITIONLEVEL,
        widget=forms.Select(attrs={'class': 'form-control'})
        )

    TYPE = (
        ("Home Tuition", "Home Tuition"),
        ("Online Tuition", "Online Tuition"),
    )

    tuition_type = forms.ChoiceField(
        choices=TYPE, 
        widget=forms.Select(attrs={'class': 'form-control'})
        )

    address = forms.CharField(max_length=300)

    hours_per_day = forms.IntegerField()
    days_per_week = forms.IntegerField()

    estimated_fees = forms.IntegerField()

    def clean_hours_per_day(self):
        hours_per_day = self.cleaned_data['hours_per_day']
        if hours_per_day > 6:
            raise ValidationError("Hours Per Day Cannot be Greater Than 6")
        return hours_per_day
    
    def clean_days_per_week(self):
        days_per_week = self.cleaned_data['days_per_week']
        if days_per_week > 7:
            raise ValidationError("Days Per Day Cannot be Greater Than 7")
        return days_per_week


class AboutStudentForm(forms.Form):
    textArea = forms.CharField(
        widget=forms.Textarea,
        max_length=300
    )
    

from .validators import validate_file_extension

class ProfilePicture(forms.Form):

    image = forms.ImageField(validators=[validate_file_extension])


    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 1*1024*1024:
                raise ValidationError("Image file too large, > 1mb ")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")
