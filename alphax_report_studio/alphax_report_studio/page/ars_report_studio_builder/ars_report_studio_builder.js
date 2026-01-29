frappe.pages['ars-report-studio-builder'].on_page_load = function(wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Report Studio Builder',
    single_column: true
  });

  $(frappe.render_template('ars_report_studio_builder', {})).appendTo(page.body);

  const $format = $('#ars_format');
  const $run = $('#ars_run');
  const $out = $('#ars_output');

  function render_lines(rows){
    const table = $(`
      <table class="table table-bordered">
        <thead><tr><th>Line</th><th class="text-right">Value</th></tr></thead>
        <tbody></tbody>
      </table>
    `);
    const tbody = table.find('tbody');
    rows.forEach(r=>{
      const indent = (r.meta && r.meta.indent) ? r.meta.indent : 0;
      const pad = '&nbsp;'.repeat(indent*4);
      const label = (r.meta && r.meta.bold) ? `<b>${pad}${frappe.utils.escape_html(r.label||'')}</b>` : `${pad}${frappe.utils.escape_html(r.label||'')}`;
      const v = (r.value===null || r.value===undefined) ? '' : frappe.format(r.value, {fieldtype:'Currency'});
      tbody.append(`<tr><td>${label}</td><td class="text-right">${v}</td></tr>`);
    });
    $out.empty().append(table);
  }

  function render_table(data){
    if(!data || !data.length){
      $out.html('<div class="text-muted">No data</div>');
      return;
    }
    const cols = Object.keys(data[0]);
    const table = $('<table class="table table-bordered table-hover"><thead></thead><tbody></tbody></table>');
    table.find('thead').append('<tr>' + cols.map(c=>`<th>${frappe.utils.escape_html(c)}</th>`).join('') + '</tr>');
    data.forEach(row=>{
      table.find('tbody').append('<tr>' + cols.map(c=>`<td>${frappe.utils.escape_html(String(row[c] ?? ''))}</td>`).join('') + '</tr>');
    });
    $out.empty().append(table);
  }

  function load_formats(){
    frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "ARS Report Format",
        fields: ["name", "title"],
        limit_page_length: 200,
        order_by: "modified desc"
      }
    }).then(r=>{
      const items = (r.message || []);
      $format.empty();
      items.forEach(i=>{
        $format.append(`<option value="${i.name}">${frappe.utils.escape_html(i.title)} (${i.name})</option>`);
      });
    });
  }

  $run.on('click', ()=>{
    const format = $format.val();
    if(!format){ frappe.msgprint('Select a format'); return; }
    frappe.call({
      method: "alphax_report_studio.api.run_report_format",
      args: {
        report_format: format,
        filters: {
          from_date: $('#ars_from').val(),
          to_date: $('#ars_to').val()
        }
      }
    }).then(r=>{
      const resp = r.message;
      if(!resp){ $out.html('<div class="text-danger">No response</div>'); return; }
      if(resp.type === "lines") render_lines(resp.data);
      else if(resp.type === "table") render_table(resp.data);
      else $out.text(JSON.stringify(resp));
    });
  });

  load_formats();
};
