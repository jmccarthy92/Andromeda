import React from 'react';
import { Container, List, Header, Divider, Header, Table, Form, Segment, Dimmer, Loader } from 'semantic-ui-react';
import MasterTable from './table';


class App extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            isLoading: true,

        };
        this.onBlur = this.onBlur.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSelectChange = this.handleSelectChange.bind(this);
    }

    componentDidMount(){
        fetch("/student_system/student_system_api/get_general_data/")
            .then((response) => {
                if(!response.ok){
                    throw Error(response.statusText);
                }

                return response;
            })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                let department_options = [];
                let time_period_options = [];
                let meeting_day_options = [];
                let semester_options = [];
                let building_options = [];
                let room_options = [];
                let faculty_options = [];
                let default_option = { key: 0, text: '------', value: true};
                semester_options.push(default_option);
                department_options.push(default_option);
                time_period_options.push(default_option);
                meeting_day_options.push(default_option);
                building_options.push(default_option);
                room_options.push(default_option);
                faculty_options.push(default_option);
                let d, f, b, t, m, r, s;
                for( let s of data.semesters){
                    let semester_data = {
                        key: s.semester_id,
                        text: s.semester_season + '-' + s.semester_year + "---"+ s.semester_status,
                        value: s.semester_id
                    };
                    semester_options.push(semester_data);
                }
                for( let d of data.departments){
                   let department_data = {
                        key:  d.department_id,
                        text: d.department_name,
                        value: d.department_id,
                    };
                    department_options.push(department_data);
                }
                for( let t of data.time_periods){
                   let time_period_data = {
                        key:  t.time_period_id,
                        text: t.time_range,
                        value: t.time_period_id,
                    };
                    time_period_options.push(time_period_data);
                }
                for( let m of data.meeting_days){
                   let meeting_day_data = {
                        key:  m.days_id,
                        text: m.day_range,
                        value: m.days_id,
                    };
                    meeting_day_options.push(meeting_day_data);
                }
                for( let b of data.buildings){

                   let buildings_data = {
                        key:  b.building_id,
                        text: b.building_name,
                        value: b.building_id,
                    };
                   building_options.push(buildings_data);
                }
                for( let r of data.rooms){
                   let room_data = {
                        key:  r.rooms_id,
                        text: r.room_number,
                        value: r.rooms_id,
                    };
                   room_options.push(room_data);
                }
                for( let f of data.faculty){
                   let faculty_data = {
                        key:  f.faculty_id,
                        text: f.full_name,
                        value: f.faculty_id,
                    };
                   faculty_options.push(faculty_data);
                }
                this.baseState = {
                    departments: department_options,
                    time_periods: time_period_options,
                    meeting_days: meeting_day_options,
                    semester: semester_options,
                    building: building_options,
                    submittedValue: false,
                    rooms: room_options,
                    faculty: faculty_options,
                    isLoading: false,
                    semester_id: false,
                    department_id: false,
                    faculty_id: false,
                    days_id: false,
                    period_id: false,
                    building_id: false,
                    room_id: false,
                    course_name: false
                };

                this.setState(this.baseState);
            })
            .catch((error) => {
                console.error(error);
            })
    }

    handleInputChange(event) {
        this.setState({
            [event.target.id]: event.target.value
        })
    }

    onBlur(){
        this.setState({
            course_name: this.state.course_name_input,
            attributeFlag: 'course_name'
        })
    }

    handleSelectChange(value, id){
        console.log(value);
        console.log(id);
        if( value === true){
            console.log(this.state);

             switch (id) {
                case 'semester_select':
                    this.setState({
                        semester_id: false
                    });
                    break;
                case 'department_select':
                    this.setState({
                        department_id: false
                    });
                    break;
                case 'faculty_select':
                    this.setState({
                        faculty_id: false
                    });
                    break;
                case 'days_select':
                    this.setState({
                        days_id: false
                    });
                    break;
                case 'time_period_select':
                    this.setState({
                        period_id: false
                    });
                    break;
                case 'building_select':
                    this.setState({
                        building_id: false
                    });
                    break;
                case 'room_select':
                    this.setState({
                        room_id: false
                    });
                    break;
            }
            if(!this.state.room_id && !this.state.building_id
                && !this.state.period_id && !this.state.days_id
                && !this.state.faculty_id && !this.state.department_id && !this.state.semester_id) {
                this.setState(this.baseState);
            }

        } else {
            let attribute_flag;
            switch (id) {
                case 'semester_select':
                    attribute_flag = 'semester';
                    this.setState({
                        semester_id: value
                    });
                    break;
                case 'department_select':
                    attribute_flag = 'department';
                    this.setState({
                        department_id: value
                    });
                    break;
                case 'faculty_select':
                    attribute_flag = 'faculty';
                    this.setState({
                        faculty_id: value
                    });
                    break;
                case 'days_select':
                    attribute_flag = 'days';
                    this.setState({
                        days_id: value
                    });
                    break;
                case 'time_period_select':
                    attribute_flag = 'time_period';
                    this.setState({
                        period_id: value
                    });
                    break;
                case 'building_select':
                    attribute_flag = 'building';
                    this.setState({
                        building_id: value
                    });
                    break;
                case 'room_select':
                    attribute_flag = 'rooms';
                    this.setState({
                        room_id: value
                    });
                    break;
            }
            console.log(value);
            this.setState({
                submittedValue: value,
                attributeFlag: attribute_flag
            });
        }
    }

    render() {



        if( this.state.isLoading){
            return(
                <Segment>
                  <Dimmer active>
                    <Loader size='massive'>Loading</Loader>
                  </Dimmer>
                </Segment>
            );
        }
        return (
            <Container >
                <Header size='huge'>Master Schedule</Header>
                <PageInformation/>
                <Form>
                    <Form.Group widths='equal'>
                        <Form.Select id='department_select' onChange={(e, {value, id}) => this.handleSelectChange(value, id)} fluid label='Department Name'  options={this.state.departments} placeholder='Department Name'/>
                        <Form.Input id='course_name_input' onBlur={this.onBlur} onChange={this.handleInputChange} fluid label='Course Name' placeholder='Course Name'/>
                    </Form.Group>
                    <Form.Select id='faculty_select' onChange={(e, {value, id}) => this.handleSelectChange(value, id)} fluid label='Faculty' options={this.state.faculty} placeholder='Faculty'/>
                    <Form.Group widths='equal'>
                        <Form.Select id='days_select' onChange={(e, {value, id}) => this.handleSelectChange(value, id)} fluid label='Meeting Days' options={this.state.meeting_days} placeholder='Meeting Days'/>
                        <Form.Select id='time_period_select' onChange={(e, {value, id}) => this.handleSelectChange(value, id)} fluid label='Time Periods' options={this.state.time_periods} placeholder='Time Periods'/>
                        <Form.Select id='semester_select' onChange={(e, {value, id}) => this.handleSelectChange(value, id)} fluid label='Semester' options={this.state.semester} placeholder='Semesters'/>
                    </Form.Group>
                    <Form.Group widths='equal'>
                        <Form.Select id='building_select' onChange={(e, {value, id}) => this.handleSelectChange(value, id)} fluid label='Buldings' options={this.state.building} placeholder='Buildings'/>
                        <Form.Select id='room_select' onChange={(e, {value, id}) => this.handleSelectChange(value, id)} fluid label='Rooms' options={this.state.rooms} placeholder='Rooms'/>
                    </Form.Group>

                </Form>
                <Divider horizontal>Results</Divider>
                { (this.state.submittedValue) &&
                    //<MasterTable search_value={this.state.submittedValue} attribute_flag={this.state.attributeFlag} />
                    <MasterTable
                        semester_id={this.state.semester_id}
                        department_id={this.state.department_id}
                        faculty_id={this.state.faculty_id}
                        days_id={this.state.days_id}
                        period_id={this.state.period_id}
                        building_id={this.state.building_id}
                        room_id={this.state.room_id}
                        course_name={this.state.course_name}

                    />
                }
            </Container>
        );
    }

}

const PageInformation = () => (

  <List bulleted>
    <List.Item>All sections taught throughout past and present semester will be displayed in the table below.</List.Item>
    <List.Item>All search queries are made asynchronously you may choose individual filters or multiple at once</List.Item>
    <List.Item>
      When clicking a row, a modal window is displayed with the following information:
      <List.List>
        <List.Item >Course Description</List.Item>
        <List.Item>Credits</List.Item>
        <List.Item>Prerequisites</List.Item>
      </List.List>
    </List.Item>
      <List.Item href='/student_system/register_course/'>If logged in as a student access the registration page by clicking here! </List.Item>
  </List>
);


export default App;