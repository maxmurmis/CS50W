document.addEventListener('DOMContentLoaded', () => {

  const emailDiv = document.querySelector('#emails-view');
  const viewDiv = document.querySelector('#view-view');

  // By default, load the inbox
  load_mailbox('inbox');

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  viewDiv.addEventListener('click', (event) => {
    if (event.target.tagName === 'BUTTON') {
      const buttonId = event.target.id; 
      const [action, emailId] = buttonId.split('-');
      
      if (action === 'archive') {
        archive(emailId);
        load_mailbox('archive')
      } else if (action ==='reply'){


        reply(emailId);
      }
    }
  });
  
  //View mail, archive and unarchive in the inbox view
  emailDiv.addEventListener('click', (event) => {
    if (event.target.tagName === 'BUTTON') {
      const buttonId = event.target.id; 
      const [action, emailId] = buttonId.split('-'); 
  
      if (action === 'open') {
        mark_as_read(emailId);
        get_email(emailId); 
      } else if (action === 'archive') {
        archive(emailId);
      } else if (action ==='unarchive') {
        unarchive(emailId);
      }
    }
  });

  // Send mail
  document.querySelector('#send').addEventListener('click', (event) => {

    event.preventDefault();
    console.log('Form submitted'); // For debugging
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;
  
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: recipients,
          subject: subject,
          body: body,
          read: false
      }),
    })
  
    .then(response => {
      return response.json();
    })
    .then(result => {
      console.log('Email send result:', result);  // Logs the result from the server
      load_mailbox('sent');
      return false
    })
    .catch(error => {
      console.error('Error during fetch:', error);  // Log fetch errors
    });

    return false
  });

  function compose_email() {

    console.log("Compose view loaded")

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#view-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
  
    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }

  function reply(id) {
    compose_email();

    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      const sender = email['sender']
      const subject= email['subject'];
      const body = email['body'];
      const timestamp = email['timestamp']

      document.querySelector('#compose-recipients').value = `${sender}`;
      document.querySelector('#compose-subject').value = `RE: ${subject}`;
      document.querySelector('#compose-body').value = `On ${timestamp}, ${sender} wrote: "${body}"`;
    })   
  }

  function load_mailbox(mailbox) {
    
    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#view-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
  
    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML=`<h3> ${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)} </h3><br>`;
    const title = document.querySelector('#emails-view').innerHTML.split(' ')[1]
    console.log(`The title is ${title}`)
    if (title==="Archive"){get_archive()}
    else if(title==="Inbox"){get_inbox()}
    else if(title==="Sent"){get_sent()}
  }

  function get_inbox(){
    fetch('/emails/inbox')
    .then(response => response.json())
    .then(emails => {
        // Print emails
        console.log(emails);

        //Shows the latest 5 mails in emailDiv
        if (emails.length === 0) {
          console.log("No emails in archive.");
          emailDiv.innerHTML = "<p>No archived emails to display.</p>";
          return;
        }
  
        // Determine the number of emails to show (minimum of emails.length and 5)
        const limit = Math.min(emails.length, 8);

        for (let i=0; i<limit; i++){
          const mail = document.createElement('div');
          mail.innerHTML= `<h6>${emails[i]['subject']}</h6>
                          <p>From: ${emails[i]['sender']}</p>
                          <p>${emails[i]['timestamp']}</p>
                          <button id="open-${emails[i]['id']}">Open</button>
                          <button id="archive-${emails[i]['id']}">Archive</button>`
          if(emails[i]['read']){mail.className= "read";} 
          else {mail.className= "not-read"}
          mail.id = `id ${emails[i]['id']}`
          emailDiv.appendChild(mail);
        }
    });
  }

  function get_sent(){
    fetch('/emails/sent')
    .then(response => response.json())
    .then(emails => {
      emailDiv.innerHTML = '';
      // Print emails
      if (emails.length === 0) {
        console.log("No emails sent.");
        emailDiv.innerHTML = "<p>No sent emails to display.</p>";
        return;
      }

      // Determine the number of emails to show (minimum of emails.length and 8)
      const limit = Math.min(emails.length, 8);

      for (let i=0; i<limit; i++){
        const mail = document.createElement('div');
        mail.innerHTML= `<h6>${emails[i]['subject']}</h6>
                        <p>To: ${emails[i]['recipients']}</p>
                        <p>${emails[i]['timestamp']}</p>
                        <button id="open-${emails[i]['id']}">Open</button>`;
        mail.className= "not-read";
        emailDiv.appendChild(mail);
      }
    });
  }

  function get_archive(){

    viewDiv.innerHTML= ""
    fetch('/emails/archive')
    .then(response => response.json())
    .then(emails => {
      if (emails.length === 0) {
        console.log("No emails in archive.");
        emailDiv.innerHTML = "<p>No archived emails to display.</p>";
        return;
      }

      // Determine the number of emails to show (minimum of emails.length and 5)
      const limit = Math.min(emails.length, 8);

      for (let i = 0; i < limit; i++) {
        const mail = document.createElement('div');
        mail.innerHTML = `<h6>${emails[i]['subject']}</h6>
                          <p>From: ${emails[i]['sender']}</p>
                          <p>${emails[i]['timestamp']}</p>
                          <button id="unarchive-${emails[i]['id']}">Unarchive</button>`;
        mail.className = "read";
        emailDiv.appendChild(mail);
      }
    })
   }

  function get_email(id){
    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      console.log(email);

      //Hide the other views
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'none';
      document.querySelector('#view-view').style.display = 'block';

      //Erase former mail
      viewDiv.innerHTML= ""

      //Create the new div that will show the mail
      const accessedMail = document.createElement('div');
      accessedMail.className='accessed-mail';

      //Assign the values of the required mail
      const sender = email['sender'];
      const recipients = email['recipients']
      const subject= email['subject'];
      const body = email['body'];
      const timestamp = email ['timestamp'];

      //Print the content of the mail on the screen
      accessedMail.innerHTML= `<h4>${subject}</h5>
      <h5>From: ${sender}</h6>
      <h5>To: ${recipients}</h6>
      <p>Sent: ${timestamp}</p>
      <br>
      <p>${body}</p>
      <br>
      <button id="reply-${id}">Reply</button>
      <button id="archive-${id}">Archive</button>`;
      viewDiv.appendChild(accessedMail);
    });
  }

  function archive(id){
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: true
      })
    })
    .then(() => {
      console.log(`Email ${id} archived.`);
      load_mailbox('inbox');
    })
  }

  function unarchive(id){
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: false
      })
    })
    .then(() => {
      console.log(`Email ${id} unarchived.`);
      load_mailbox('inbox');
    })
  }

  function mark_as_read(id){
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
        })
    })
  }
  return false
});


