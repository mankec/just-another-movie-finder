import Alpine from 'alpinejs';

export function searchSelectMultiple(event, listName) {
  const searchValue = event.currentTarget.value.toLowerCase();
  const list = document.querySelector(`#${listName}_list`);
  const listItems = list.querySelectorAll("li");
  listItems.forEach(item => {
    const label = item.querySelector("div label");
    const text = label.textContent.toLowerCase();

    if (text.startsWith(searchValue)) {
      item.classList.remove("hidden");
    } else {
      item.classList.add("hidden");
    }
  });
}

Alpine.magic('searchSelectMultiple', () => searchSelectMultiple);
