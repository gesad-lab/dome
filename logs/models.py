from django.db import models


class streaming(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    text = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"


class pokemon(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class equipment(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    sector = models.CharField(max_length=200, null=True, blank=True)
    manager = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class new_company(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    owner = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class company(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    owner = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class course(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class blockade(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    localization = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.localization}"


class person(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class article(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    year = models.CharField(max_length=200, null=True, blank=True)
    year1 = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    co_author = models.CharField(max_length=200, null=True, blank=True)
    coauthor = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    set = models.CharField(max_length=200, null=True, blank=True)
    keywords = models.CharField(max_length=200, null=True, blank=True)
    revision = models.CharField(max_length=200, null=True, blank=True)
    abstract = models.CharField(max_length=200, null=True, blank=True)
    circulation = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.title} | {self.year} | {self.email}"


class show(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    date = models.CharField(max_length=200, null=True, blank=True)
    place = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.date} | {self.place}"


class former_student(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class student(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    table = models.CharField(max_length=200, null=True, blank=True)
    database = models.CharField(max_length=200, null=True, blank=True)
    age = models.CharField(max_length=200, null=True, blank=True)
    lastname = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    update = models.CharField(max_length=200, null=True, blank=True)
    skin = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.email} | {self.table}"


class sku(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class subject(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    professor = models.CharField(max_length=200, null=True, blank=True)
    semester = models.CharField(max_length=200, null=True, blank=True)
    main_reference = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.professor} | {self.semester}"


class pizza(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    flavour = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.flavour}"


class cream(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    ice = models.CharField(max_length=200, null=True, blank=True)
    flavour = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.ice} | {self.flavour}"


class product(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.type}"


class film(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    running = models.CharField(max_length=200, null=True, blank=True)
    genre = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    year = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.title} | {self.running} | {self.genre}"


class teacher(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class invoice(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    value = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.value}"


class car(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    license = models.CharField(max_length=200, null=True, blank=True)
    color = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.license} | {self.color}"


class book(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    publish = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.publish}"


class city(models.Model):
    dome_created_at = models.DateTimeField(auto_now_add=True)
    dome_updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    population = models.CharField(max_length=200, null=True, blank=True)
    number = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"