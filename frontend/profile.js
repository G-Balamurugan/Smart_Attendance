const initializeProfile = () => {
    var info = localStorage.getItem('employeeDetails')
    info = JSON.parse(info)
    console.log(info.first_name)
    // const info = {
    //     'first_name': 'Mohamed', 
    //     'last_name': 'Asif', 
    //     'age': '20', 
    //     'designation': 'DevOps Engineer', 
    //     'emp_id': '8726487', 
    //     'dob': '10-09-2002', 
    //     'email': 'manojganesan@gmail.com', 
    //     'attendance_percent': '86 %', 
        
    // }

    const details = document.createElement('div')
    details.classList.add('details')

    const row = document.createElement('div')
    row.classList.add('flex-row')

    const end = document.createElement('div')
    end.classList.add('flex-column')
    end.classList.add('end')
    
    const column = document.createElement('div')
    column.classList.add('flex-column')
    column.classList.add('right')

    // Div
    var container = document.createElement('div')
    // Field
    var field = document.createElement('p')
    field.classList.add('field')
    field.textContent = "First Name"
    // Value
    var value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.first_name
    container.appendChild(field)
    container.appendChild(value)
    column.appendChild(container)

    // Div
    container = document.createElement('div')
    field = document.createElement('p')
    field.classList.add('field')
    field.textContent = "Last Name"
    value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.last_name
    container.appendChild(field)
    container.appendChild(value)
    column.appendChild(container)

    container = document.createElement('div')
    field = document.createElement('p')
    field.classList.add('field')
    field.textContent = "DOB"
    value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.dob
    container.appendChild(field)
    container.appendChild(value)
    column.appendChild(container)

    container = document.createElement('div')
    field = document.createElement('p')
    field.classList.add('field')
    field.textContent = "EID"
    value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.emp_id
    container.appendChild(field)
    container.appendChild(value)
    column.appendChild(container)

    end.appendChild(column)
    
    // Next Column
    const anotherColumn = document.createElement('div')
    anotherColumn.classList.add('flex-column')

    container = document.createElement('div')
    field = document.createElement('p')
    field.classList.add('field')
    field.textContent = "Designation"
    value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.designation
    container.appendChild(field)
    container.appendChild(value)
    anotherColumn.appendChild(container)

    container = document.createElement('div')
    field = document.createElement('p')
    field.classList.add('field')
    field.textContent = "Age"
    value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.age
    container.appendChild(field)
    container.appendChild(value)
    anotherColumn.appendChild(container)

    container = document.createElement('div')
    field = document.createElement('p')
    field.classList.add('field')
    field.textContent = "Email"
    value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.email
    container.appendChild(field)
    container.appendChild(value)
    anotherColumn.appendChild(container)

    row.appendChild(end)
    row.appendChild(anotherColumn)
    details.appendChild(row)

    // Attendance Percentage
    const centerDiv = document.createElement('div')
    centerDiv.classList.add('center')

    const attendanceDiv = document.createElement('div')
    attendanceDiv.classList.add('attendance')

    field = document.createElement('p')
    field.classList.add('field')
    field.classList.add('large')
    field.textContent = "Attendance : "
    value = document.createElement('p')
    value.classList.add('value')
    value.textContent = info.attendance_percent

    attendanceDiv.appendChild(field)
    attendanceDiv.appendChild(value)
    centerDiv.append(attendanceDiv)
    details.appendChild(centerDiv)

    document.querySelector('.profile').appendChild(details)
}

const checkIfLoggedIn = () => {
    const token = localStorage.getItem('token')
    if (!token) {
        window.location.href = './login.html'
    }
}

checkIfLoggedIn()
initializeProfile()