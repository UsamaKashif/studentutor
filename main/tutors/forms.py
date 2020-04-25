from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from django import forms
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from .models import Tutor, PostAnAd

class TutorSignUpform(UserCreationForm):

    GENDER = (
        ("Male", "Male"),
        ("Female", "Female")
    )
    
    age = forms.IntegerField()
    city = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    cnic = forms.CharField(max_length=13)
    gender = forms.CharField(max_length=6)
    phone=forms.CharField(max_length=11)

    class Meta :
        model = User
        fields = ["username", "phone",'password1', 'password2', 'email', "age", "city", 'first_name', 'last_name', "gender","cnic"]

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Account with that email already exists")
        return email
    
    def clean_cnic(self):
        cnic = self.cleaned_data['cnic']
        if len(cnic) < 13 or cnic.isdigit() != True:
            raise ValidationError("CNIC must be of 13 digits")
        return cnic

    def clean_gender(self):
        gender = self.cleaned_data['gender']
        if not(gender.lower() == "male" or  gender.lower() == "female"):
            raise ValidationError("Gender should be Male/Female")

        return gender

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) < 11 or phone.isdigit() != True:
            raise ValidationError("Phone Number must be of 11 digits")
        return phone


class TutorProfile (ModelForm):
    class Meta:
        model = Tutor
        fields = "__all__"
        exclude = ['tutor']


class PostAnAdForm(forms.Form):

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

    subject = forms.ChoiceField(choices=SUBJECT,widget=forms.Select(attrs={'class': 'form-control'}))
    tuition_level = forms.ChoiceField(choices=TUITIONLEVEL,widget=forms.Select(attrs={'class': 'form-control'}))


    CANTRAVEL = (
        ("Yes", "Yes"),
        ("No", "No"),
    )

    can_travel = forms.ChoiceField(choices=CANTRAVEL,widget=forms.Select(attrs={'class': 'form-control'}))
    estimated_fees = forms.IntegerField()
    address = forms.CharField(max_length=300)


class AboutForm(forms.Form):
    tagline = forms.CharField(max_length=50, required=True)
    about = forms.CharField(max_length=300,widget=forms.Textarea,required=True)

class QualificationForm (forms.Form):

    QUALIFICATIONS = (
        ("Masters in computer science", "Masters in computer science"),
        ("MBA", "MBA"),
        ("Bachelors in Engineering", "Bachelors in Engineering"),
        ("B-Com", "B-Com"),
        ("BBA","BBA"),
        ("Bachelors in Science", "Bachelors in Science"),
        ("BA", "BA"),
        ("PhD","PhD"),
        ("ACCA", "ACCA"),
        ("Chartered Accountant (CA)","Chartered Accountant (CA)"),
        ("CFA","CFA"),
        ("CIMA","CIMA"),
        ("MBBS","MBBS"),
        ("BDS","BDS"),
        ("A level", "A level"),
        ("O level", "O level"),
        ("Intermediate", "Intermediate"),
        ("Matric", "Matric"),
        ("MSC", "MSC"),
        ("MA Economics","MA Economics"),
        ("MS", "MS"),
        ("Masters in Commerce", "Masters in Commerce"),
        ("Bachelors in Computer Science","Bachelors in Computer Science"),
        ("Doctorate", "Doctorate"),
        ("M. Ed", "M. Ed"),
        ("Masters in English", "Masters in English"),
        ("DPT", "DPT"),
        ("M Phil", "M Phil"),
        ("MA", "MA")
    )

    highest_qual = forms.ChoiceField(
        choices=QUALIFICATIONS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
        )
    highest_qual_inst = forms.CharField(max_length=100, required=True)

    secondary_qaul = forms.ChoiceField(
        choices=QUALIFICATIONS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
        )
    secondary_qaul_inst = forms.CharField(max_length=100, required=True)

from .validators import validate_file_extension

class ProfilePicture(forms.Form):

    image = forms.ImageField(validators=[validate_file_extension], required=True)

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 1*1024*1024:
                raise ValidationError("Image file too large, > 1mb ")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")


class VerifyForm(forms.Form):
    cnic_front = forms.ImageField(validators=[validate_file_extension])
    cnic_back = forms.ImageField(validators=[validate_file_extension])

    highest_qual = forms.ImageField(validators=[validate_file_extension])