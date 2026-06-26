from django import forms

class HairtypeForm(forms.ModelForm):

    HAIR_PATTERN_CHOICES = [
        ('straight', 'Straight - Type 1 (No natural curl)'),
        ('wavy', 'Wavy - Type 2 (Loose S-patterns)'),
        ('curly', 'Curly - Type 3 (Defined spirals)'),
        ('coily', 'Coily - Type 4 (Z-angles & tight coils)'),
    ]

    STRAND_THICKNESS_CHOICES = [
        ('fine', 'Fine (Delicate, easily weighed down)'),
        ('medium', 'Medium (Standard strand structural profile)'),
        ('coarse', 'Coarse (Thick diameter, high density strength)'),
    ]

    SCALP_CONDITION_CHOICES = [
        ('dry_flaky', 'Dry / Flaky (Needs hyper-hydration lipids)'),
        ('normal_balanced', 'Normal / Balanced'),
        ('oily', 'Oily (Requires dynamic clarifying sebum regulation)'),
    ]

    hair_pattern = forms.ChoiceField(choices=HAIR_PATTERN_CHOICES,
                                     widget=forms.RadioSelect(attrs={'class':'hair-pattern-radio'}),
                                     label='1. Identify Your Hair Pattern'
                                     )
