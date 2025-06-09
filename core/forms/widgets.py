from django.forms.widgets import CheckboxSelectMultiple, RadioSelect
from django.utils.safestring import mark_safe
from django.utils.html import format_html, format_html_join


class PrettyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        html = []
        html.append(
            format_html("""
                <div class="bg-white rounded-lg shadow-sm w-60 dark:bg-gray-700">
                <div class="p-3">
                    <label for="input-group-search" class="sr-only">Search</label>
                    <div class="relative">
                    <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
                        <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
                    </svg>
                    </div>
                    <input type="text" id="input-group-search" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5  dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="{placeholder}">
                    </div>
                </div>
                <ul class="h-38 px-3 pb-3 overflow-y-scroll text-sm text-gray-700 dark:text-gray-200" aria-labelledby="dropdownSearchButton">
                """,
                placeholder=self.attrs["placeholder"]
            )
        )
        html.append(
            format_html_join(
                "\n",
                """
                <li>
                <div class="flex items-center p-2 rounded-sm hover:bg-gray-100 dark:hover:bg-gray-600">
                    <input
                        id="{name}_{value}"
                        type="checkbox"
                        value="{value}"
                        name="{name}"
                        class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500"
                    >
                    <label for="{name}-{value}" class="w-full ms-2 text-sm font-medium text-gray-900 rounded-sm dark:text-gray-300">{label}</label>
                </div>
                </li>
                """,
                (
                    {
                        "value": value,
                        "name": name,
                        "label": label,
                    }
                    for value, label in self.choices),
            )
        )
        html.append("</ul></div>")
        return mark_safe("".join(html))


class PrettyRadioSelect(RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        html = []
        html.append("<div class='flex flex-col gap-y-3'>")
        html.append(
            format_html_join(
                "\n",
                """
                <div class="flex">
                    <div class="flex items-center h-5">
                        <input
                            id="radio_button_{value}"
                            type="radio"
                            value="{value}"
                            name="{name}"
                            {checked}
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                        >
                    </div>
                    <div class="ms-2 text-sm">
                        <label for="{value}" class="font-medium text-gray-900 dark:text-gray-300">{label}</label>
                        {helper}
                    </div>
                </div>
                """,
                (
                    {
                        "value": value,
                        "label": label,
                        "name": self.attrs["name"], # TODO: Use 'name' from params
                        "checked": "checked" if value == self.attrs["checked"] else "",
                        "helper": format_html("""
                            <p 
                                id="helper-radio-text"
                                class="text-xs font-normal text-gray-500 dark:text-gray-300"
                            >
                                {helper_text}
                            </p>
                            """,
                            helper_text=self.attrs.get("helpers").get(value)
                        ) if self.attrs.get("helpers").get(value) else "",
                    }
                    for value, label in self.choices
                ),
            )
        )
        html.append("</div>")
        return mark_safe("".join(html))
