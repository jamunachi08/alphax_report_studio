frappe.pages['ars-wizard'].on_page_load = function(wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'AlphaX Report Wizard',
    single_column: true
  });

  const $body = $(page.body);
  $body.append(`
    <div class="card p-4">
      <div class="row">
        <div class="col-md-6">
          <label class="form-label">Report Name</label>
          <input type="text" class="form-control" id="ars_report_name" placeholder="e.g. NISA MIS – LOB Breakdown">
        </div>
        <div class="col-md-3">
          <label class="form-label">Dataset</label>
          <input type="text" class="form-control" id="ars_dataset" placeholder="e.g. NISA_GL_BASE">
          <div class="text-muted small mt-1">Leave blank to use default from ARS Settings.</div>
        </div>
        <div class="col-md-3">
          <label class="form-label">Report Type</label>
          <select class="form-control" id="ars_report_type">
            <option>Table</option>
            <option>Pivot</option>
            <option>Chart</option>
            <option>KPI</option>
          </select>
        </div>
      </div>

      <div class="mt-3">
        <button class="btn btn-primary" id="ars_create_btn">Create Report</button>
        <span class="ml-2 text-muted" id="ars_status"></span>
      </div>

      <hr/>
      <div class="text-muted">
        Next step: open the created <b>ARS Report Format</b> and click <b>Run</b>.
      </div>
    </div>
  `);

  // Link field lookups (non-mandatory)
  frappe.ui.form.make_control({
    df: {fieldtype: 'Link', options: 'ARS Dataset', fieldname: 'dataset', label: 'Dataset'},
    parent: $body.find('#ars_dataset').parent(),
    render_input: true,
  });

  $('#ars_create_btn').on('click', () => {
    const name = $('#ars_report_name').val();
    const dataset = $('#ars_dataset').val();
    const report_type = $('#ars_report_type').val();

    if (!name) {
      frappe.msgprint('Please enter Report Name');
      return;
    }

    $('#ars_status').text('Creating...');
    frappe.call({
      method: 'alphax_report_studio.wizard.wizard_create_report',
      args: {report_name: name, dataset: dataset || null, report_type: report_type},
    }).then(r => {
      $('#ars_status').text('Created: ' + r.message.name);
      frappe.set_route('Form', 'ARS Report Format', r.message.name);
    }).catch(() => {
      $('#ars_status').text('');
    });
  });
};
