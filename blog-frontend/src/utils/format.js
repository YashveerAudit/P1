const dateFormatter = new Intl.DateTimeFormat(undefined, {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
});

export const formatDate = (iso) => dateFormatter.format(new Date(iso));

export const excerpt = (text, length = 160) =>
  text.length <= length ? text : `${text.slice(0, length).trimEnd()}…`;
