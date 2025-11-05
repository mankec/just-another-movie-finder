import Alpine from 'alpinejs';

export function submitForm(form) {
  form.submit()
}

Alpine.magic('submitForm', () => submitForm);
