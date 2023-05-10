
import {React,useState,useEffect} from 'react';
import { LockOutlined, UserOutlined ,EyeTwoTone, EyeInvisibleOutlined,MailOutlined} from '@ant-design/icons';
import { Button, Checkbox, Form, Input, Alert , Row,Col,message} from 'antd';


import './Login.less';
// eslint-disable-next-line
import {to_auth} from '../utils';
import {AUTH_ROOT} from '../branding'
// import Countdown from 'antd/lib/statistic/Countdown';
// eslint-disable-next-line
// const [passwordVisible, setPasswordVisible] = useState(false);

// const { Option } = Select;
// const { Search } = Input;


const onFinish = (values) => {
    // let [html,sethtml] = useState(null);
    // console.log('Received values of form: ', values);
    let data = values
    let type
    if(data.verify_code !== undefined)
    {
        type = "register"
    }
    else if(data.verify_code===undefined)
    {
        type = "login"
    }
    return new Promise((resolve)=>{
        fetch(AUTH_ROOT+'normal/'+type,{
            method: 'POST',
            redentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: data ? JSON.stringify(data) : '{}',
        }).then((res)=>{
            if(res.status!==200)
                return {
                    'error_msg': '出错拉',
                };
            else
                return res.redirected ? window.location.href = "/": res.json();
        }).then((json)=>{
            resolve(json);
            
            message.error({content: json.message, key: 'Board.ManualLoadData', duration: 2});
            
        })
        .catch((e)=>{
            resolve({
                'error': 'error',
            });
        });
    })
};

export function LoginForm(props)
{
    // console.log(props)
    const {SetIsshow} = props;
    return(
        <Form
        name="normal_login"
        className="login-form"
        initialValues={{ remember: true, urlfor:"Login"}}
        onFinish={onFinish}
        >
        <Form.Item
            name="mail"
            rules={[
                { 
                    required: true, message: '请输入账号喵！' },
                {
                    pattern: /^[a-zA-Z0-9_.-]+@|mail.dhu.edu.cn|r00team.cc|$/,
                    message: '邮箱格式不正确',
                },
                {
                    max: 50,
                    message: '邮箱不得超过50字符',
                },
            ]}
        >
            <Input prefix={<UserOutlined className="site-form-item-icon" />} placeholder="邮箱" />
        </Form.Item>
        <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码喵！' }]}
        >
            <Input
            prefix={<LockOutlined className="site-form-item-icon" />}
            type="password"
            placeholder="密码"
            />
        </Form.Item>
        {/* <Form.Item>
            <Form.Item name="remember" valuePropName="checked" noStyle>
            <Checkbox>记住密码</Checkbox>
            </Form.Item>

            <a className="login-form-forgot" href="/">
            忘记密码请联系管理员喔
            </a>
        </Form.Item> */}

        <Form.Item>
            <Button type="primary" htmlType="submit" className="login-form-button">
            Log in
            </Button>
            Or <a onClick={()=>SetIsshow(true)}>Register Now!</a>
        </Form.Item>
        </Form>
    );
    
}
// function toRegister(e)
// {
//     console.log(e);
//     IsShow = !IsShow;
// }

const useCountDown = s => {
    const [seconds, setSeconds] = useState(s);
    // console.log(seconds)
    useEffect(() => {
      setTimeout(() => {
        if (seconds > 0) {
          setSeconds(seconds - 1);
        }
      }, 1000);
    }, [seconds]);
  
    return [seconds, setSeconds];
  };
  
const sendMail= async (e)=>
{
    // console.log("sendmail:",e)
    let email = {
        'mail':e
    }
    const res_1 = await new Promise((res) => {
        fetch(AUTH_ROOT + 'normal/send_mail', {
            method: 'POST',
            redentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: email ? JSON.stringify(email) : '{}'
        }).then((res)=>{
            if(res.status!==200)
                return {
                    'error_msg': '出错拉',
                };
            else
                return res.json();
        }).then((res=>{
            // console.log(res)
            if(res.status === 1)
            {
                message.error({content: res.message, key: 'Board.ManualLoadData', duration: 2});
            }else if (res.status === 0)
            {
                message.success({content: res.message, key: 'Board.ManualLoadData', duration: 2});
            }
        }));
    });
    if (res_1.status !== 200) {
        return false;
    }

    else
        return true;
    // return true;
}



// 注册组件
// eslint-disable-next-line
function RegisterForm() 
{
    const [form] = Form.useForm();
    const [ seconds,setSeconds ] = useCountDown(0);
    const [ mail,setmail ] = useState("");
    
    //监听表单变化，更新email
    const onValuesChange=(e)=>{
        if(e.mail!==null){
            setmail(e.mail)
        }
        // console.log(e)
    }

    const CheckButton = async (s,e)=>{
        const values = await form.validateFields(['mail']);
        // console.log(e)
        if(e == undefined || e == "")
        {
            return;
        }
        setSeconds(s);
        sendMail(e);
    }
    return(
        <Form
        form={form}
        name="normal_register"
        className="login-form"
        initialValues={{'type':'login'}}
        onFinish={onFinish}
        onValuesChange={onValuesChange}
        >
        <Form.Item
            name="mail"
            rules={[
                { 
                    required: true, message: '请输入账号喵！' },
                {
                    pattern: /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/,
                    message: '邮箱格式不正确',
                },
                {
                    max: 50,
                    message: '邮箱不得超过50字符',
                }
            ]}
        >
            <Input prefix={<UserOutlined className="site-form-item-icon" />} placeholder="邮箱" />
        </Form.Item>
        <Form.Item style={{marginBottom:0}}>
        <Row gutter={4}>
          <Col span={17}>
            <Form.Item             
                name="verify_code"
                // label="Phone Number"
                rules={[
                    {
                        required: true, message: 'Please input your phone number!' 
                    }, 
                    {
                        pattern: /^[0-9]{6}$/,
                        message: '请输入正确的验证码'

                    }
                ]}>
                    <Input prefix={<MailOutlined className="site-form-item-icon" />} style={{ width: '100%' }} />
                </Form.Item>
          </Col>
          <Col span={7} style>
          <Button 
                placeholder="验证码"
                type="default"
                size="default" 
                onClick={() => {CheckButton(70,mail)}}
                disabled={seconds!==0?true:false}
                style={{width:'100%'}}
            >
                {seconds > 0 ? `${seconds}s` : "获取验证码"}
            </Button>
          </Col>
        </Row>
      </Form.Item>


        <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码喵！' },
            {pattern:/^(?=.*[A-Za-z])(?=.*\d).{8,}$/,message:"密码长度至少8位并包括数字和字母哦~"},
        ]}
        >
            <Input.Password
            prefix={<LockOutlined className="site-form-item-icon" />}
            type="password"
            placeholder="密码"
            iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
            />
        </Form.Item>

        <Form.Item
            name="confirm_password"
            dependencies={['password']}
            rules={[{ required: true, message: '请输入密码喵！' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次密码输入不一样喵！'));
                },
              }),
            ]}
        >
            <Input.Password
            prefix={<LockOutlined className="site-form-item-icon" />}
            type="password"
            placeholder="二次密码"
            iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
            />
        </Form.Item>

        <Form.Item>
        <Button type="primary" htmlType="submit" className="login-form-button">
                Register！
        </Button>
        </Form.Item>
        </Form>
    );
        
}

export function Login() {
    let [isShow,setisShow] = useState(false);
    const SetIsshow = (status)=>{
        setisShow(status)
    }
  return (
    <div className="slim-container">
                    <Alert showIcon message={<b>注意</b>} description={<>
                <p>
                    请使用东华大学邮箱（学号@mail.dhu.edu.cn）注册喔~如果忘记密码请及时联系管理员！
                </p>
            </>} />
            
        <div className="login-content">
            <div className="Form" style={isShow ? { display: 'none' } : null}>
                <LoginForm  SetIsshow={SetIsshow}/>
            </div>
            

            <div className="Form" style={!isShow ? { display: 'none' } : null} >
                <RegisterForm status={false}/>
            </div>
        </div>
    </div>
  )
    
}
