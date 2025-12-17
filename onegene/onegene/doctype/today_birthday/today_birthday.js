// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on("Today Birthday", {
    refresh(frm) {
        frappe.call({
            method: 'onegene.onegene.doctype.today_birthday.today_birthday.birthday_list',
            callback: function(r) {
                if (r.message) {
                    let birthday_message;
                    if (r.message === "No Birthdays Today") {
                        birthday_message = '<div style="text-align: center;"><h2>No Birthdays Today</h2></div>';
                    } else {
                        birthday_message = `<div id="birthdayCarousel" class="carousel slide" data-ride="carousel" data-interval="4000">
                                            <div class="carousel-inner">`;

                        r.message.forEach(function(item, index) {
                            birthday_message += `<div class="carousel-item ${index == 0 ? 'active' : ''}">
                                                ${item}
                                                </div>`;
                        });
                        // birthday_message += '<li>' + item + '</li>'
                    }
                    frm.fields_dict.birthday_wish.$wrapper.empty().append(birthday_message);
                    setTimeout(function() {
                        $('#birthdayCarousel').carousel();
                    }, 500);
                } else {
                    console.log("No birthday message received.");
                }
            }
        });
    }
});
