import React from 'react';
import Nav from './components/container/Nav.jsx';
import { Card, Icon } from 'semantic-ui-react';
import FaGraduationCap from 'react-icons/lib/fa/graduation-cap';
import FaBriefcase from 'react-icons/lib/fa/briefcase';
import FaAdn from 'react-icons/lib/fa/adn';
import FaBarChart from 'react-icons/lib/fa/bar-chart';

class Index extends React.Component {

    constructor(props){
        super(props);
    }

    render() {
        var user_type = '';
        if(this.props.is_admin){
            user_type='Admin';
        } else if (this.props.is_student){
            user_type='Student'
        } else if (this.props.is_faculty){
            user_type='Faculty'
        } else {
            user_type='Researcher'
        }

        return <div className="m-top8">
                <Nav
                    is_admin={this.props.is_admin}
                    is_ft_student={this.props.is_full_time_student}
                    is_pt_student={this.props.is_part_time_student}
                    is_researcher={this.props.is_researcher}
                    is_ft_faculty={this.props.is_full_time_faculty}
                    is_pt_faculty={this.props.is_part_time_faculty}
                    is_faculty={this.props.is_faculty}
                    is_student={this.props.is_student}
                />

                {/*<DropdownExampleSelection/>*/}
                <Card fluid  color='black' style={{backgroundColor: 'rgba(255, 255, 255, 0.92)!important'}} >
                    <Card.Content extra>
                        { this.props.is_student &&
                            (<FaGraduationCap size='50' />)
                        }
                        { this.props.is_faculty &&
                            (<FaBriefcase size='50'/>)
                        }
                        { this.props.is_admin &&
                            (<FaAdn size='50'/>)
                        }
                        { this.props.is_researcher &&
                            (<FaBarChart size='50'/>)
                        }
                        <h1 style={{display: 'inline', marginLeft: '2rem'}}>{'Welcome ' + this.props.first_name + ' ' + this.props.last_name +'!'}</h1>
                    </Card.Content>
                    <Card.Content header='User Type: ' description={user_type}/>
                    <Card.Content header='Username: ' description={this.props.username}/>
                    <Card.Content header='Name: ' description={this.props.first_name + ' ' + this.props.last_name}/>
                    <Card.Content header='Emaill: ' description={this.props.email}/>
                </Card>
            </div>
    }
}

export default Index;
