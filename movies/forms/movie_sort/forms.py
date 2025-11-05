from django import forms


class MovieSortForm(forms.Form):
    DEFAULT_SORTING_KEY = "oldest"
    choices = [
        ("oldest", "Oldest"),
        ("newest", "Newest"),
        ("most_popular", "Most popular"),
        ("least_popular", "Least popular"),
        ("most_voted", "Most voted"),
        ("least_voted", "Least voted"),
        ("longest", "Longest"),
        ("shortest", "Shortest"),
    ]
    sorting_key = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": """
                bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                """,
                "x-data": "",
                "@change": "$submitForm($event.currentTarget.form);",
            }
        ),
        choices=choices,
        required=False,
        label="Sort by",
    )
