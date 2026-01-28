frappe.ui.form.on('ARS Report Format', {
  refresh(frm){
    if(!frm.is_new()){
      frm.add_custom_button('Open Builder', ()=>{
        frappe.set_route('ars-report-studio-builder');
      });
    }
  }
});
