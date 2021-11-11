const express = require('express')
const {spawn} = require('child_process');
const app = express()
const path = require('path')
const EventEmitter = require('events')
const emitter = new EventEmitter()
const db = require('./models')

const {User} = require('./models')

express.static(path.join(__dirname,'static'))
app.use(express.urlencoded({ extended:true }))

const python = spawn('python', ['imports.py']);
let dataToSend = ""

python.stdout.on('data', function (data) {
    console.log('Pipe data from python script ...');
    dataToSend = data.toString();
    console.log(dataToSend)
    let task = dataToSend.split('\n')
    task.pop()
    signal = task.pop()
    console.log(task)
    if(signal == 'DONE\r'){
        console.log('recieved')
        emitter.emit('recieved')
    }
});

python.stderr.on('data',function(data){
    console.log('ERROR')
    console.log(data.toString())
})

let gotten = false
emitter.on('recieved',()=>{gotten=true})

app.get('/',(req,res)=>{
    console.log('HOME')
    res.sendFile(path.join(__dirname,'static','signin.html'))
})

app.post('/',(req,res)=>{
    console.log('LOGIN')
    console.log(req.body)

    User.findOne({
        where:{
            email:req.body.email,
            password:req.body.password
        }
    }).then((user)=>{
        if(!user) res.redirect('/')
        else{
            if(user.isrecruiter==="true") res.redirect('/recruiter')
            else res.redirect('/candidate')
        }
    }).catch((err)=>{
        console.log(err)
        res.send(500)
    })
})

app.get('/candidate',(req,res)=>{
    console.log('CANDIDATE')
    res.sendFile(path.join(__dirname,'static','candidate.html'))
})

app.post('/candidate',(req,res)=>{
    console.log('CANDIDATE DETAILS',req.body)
    console.log(`'${req.body}'`)
    
    python.stdin.write('DATA\n')
    python.stdin.write(`${JSON.stringify(req.body)}\n`)
    
    let timer = setInterval(()=>{
        if(gotten){
            clearInterval(timer)
            gotten = false
            console.log(dataToSend)
            res.redirect('/result')
        }
    },1000)
})

app.get('/recruiter',(req,res)=>{
    console.log('RECRUITER')
    res.sendFile(path.join(__dirname,'static','candidate.html'))
})

app.post('/recruiter',(req,res)=>{
    console.log('RECRUITER DETAILS')
    User.create({
        firstname: req.body.firstname,
        lastname: req.body.lastname,
        email: req.body.email,
        password: req.body.password,
        isrecruiter: req.body.recruiter || "false"
    })
    
    res.redirect('/')
})

app.get('/register',(req,res)=>{
    console.log('REGISTER')
    res.sendFile(path.join(__dirname,'static','register.html'))
})

app.post('/register',(req,res)=>{
    console.log('REGISTER DETAILS')
    User.create({
        firstname: req.body.firstname,
        lastname: req.body.lastname,
        email: req.body.email,
        password: req.body.password,
        isrecruiter: req.body.recruiter || "false"
    })
    
    res.redirect('/')
})

app.get('/result',(req,res)=>{
    console.log('RESULT')

    python.stdin.write('PROCESS\n')
    // python.stdin.write('9493\n')

    let timer = setInterval(()=>{
        if(gotten){
            clearInterval(timer)
            gotten = false
            res.send(dataToSend)
        }
    },4000)
})

app.get('/check',(req,res)=>{
    python.stdin.write('CHECK\n')

    let timer = setInterval(()=>{
        if(gotten){
            res.send(dataToSend)
            clearInterval(timer)
            gotten = false
        }
    },1000)
})


db.sequelize.sync().then((req)=>{
    app.listen(3000,()=>{
        console.log('App running on 3000')
    })
})