import pytest

def test_equal_or_not_equal():
    a=10
    b=20
    assert a==10
    assert a!=b

def test_is_instance():
    a=10
    assert isinstance(a,int)
    b="this is the string"
    assert isinstance(b,str)

def test_boolean():
    a=10
    b=20
    assert a>5 and b>15
    assert a<15 or b<15

def test_type():
    a=10
    assert type(a)==int
    b="this is the string"
    assert type(b)==str
def test_greater_than():
    a=10
    b=20
    assert a>5
    assert b>15

def test_list():
    a=[1,2,3,4,5]
    assert 3 in a
    assert 6 not in a


class Student:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        major: str,
        years: int
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

def test_person_initialize():
    student = Student("John", "Doe", "Computer Science", 2)
    assert student.first_name == "John","first name should be John"
    assert student.last_name == "Doe" ,"last name should be Doe"
    assert student.major == "Computer Science"
    assert student.years == 2