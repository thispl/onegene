frappe.ui.form.on('Tool', {
// 	tool_name(frm) {
// 	    frm.set_value('title', frm.doc.tool_name)
// 	}

refresh(frm){
    if (!frm.doc.__islocal) {
        frm.set_df_property("tool_life", "read_only", 1);
        frm.set_df_property("total_processed_qty", "read_only", 1);
        frm.set_df_property("custom_balance_life", "read_only", 1);
    }
    if(frm.doc.custom_balance_life == 0){
        
        frm.add_custom_button("Refurbish",()=>{
            frappe.confirm("Do you want to refurbish the tool?",
            ()=>{
                
                frm.set_value("total_processed_qty",0)
                frm.save()
                .then(()=>{
                    
                    
                    frm.add_child('custom_refurbishment_log', {
                "date":frappe.datetime.get_today(),
                "approval":frappe.session.user,
                // "balance_life": frm.doc.custom_balance_life
                });

                frm.refresh_field('custom_refurbishment_log');
                
                frm.save()
                    
                    
                    
                })
                
                
            

                

            },
            
            
            
            
            )
            
        })
        
    }
    
    if(frm.doc.status != "Scrap"){
    frm.add_custom_button("Scrap",()=>{
        frappe.confirm("Do you want to mark the tool as Scrap?",
        ()=>{
            
            frm.set_value("custom_scrapbox",1)
            frm.set_value("status","Scrap")
            
            frm.save()
        }
        )
    })
    
    }
    
    
    
    
},

// custom_balance_life(frm){
    
//     if (frm.doc.status === "Scrap") {
//     return;
//   }

    
    
    
//     if(frm.doc.custom_balance_life==0){
//         frm.set_value("status","Inactive")
//     }
//     else{
//       frm.set_value("status","Active") 
//     }
//     },

tool_life(frm){
    
    frm.trigger("calculate_balance_life")
},

total_processed_qty(frm){
    
    frm.trigger("calculate_balance_life")
    
},

calculate_balance_life(frm){
    
    frm.set_value("custom_balance_life",frm.doc.tool_life - frm.doc.total_processed_qty)
}

})