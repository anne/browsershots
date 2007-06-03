from django import template
from django.db import connection

register = template.Library()

TABLE_TEMPLATE = """
<p class="debug"><a onclick="document.getElementById('sql-queries').style.visibility='visible'" href="#sql" name="sql">%s</a></p>
<table class="debug" id="sql-queries" style="visibility:hidden">
<thead>
<tr><th>%s</th><th>%s</th></tr>
</thead>
<tbody>
%s
</tbody>
</table>
""".strip()


@register.simple_tag
def sql_queries():
    if not connection.queries:
        return ''
    rows = []
    for index, query in enumerate(connection.queries):
        rows.append('<tr class="%s"><td>%s</td><td>%s</td></tr>' % (
            'row%d' % (index % 2 + 1),
            query['time'],
            query['sql'].replace('","', '", "'),
            ))
    return TABLE_TEMPLATE % (
        _("Database queries"),
        _("Time"),
        _("Database queries"),
        '\n'.join(rows),
        )