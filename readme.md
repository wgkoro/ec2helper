## This script helps you to deploy web application to EC2 instances.

This script will 

1. Check instances which have specific name.If the instances are stopped, wake them up.
2. Deploy application using capistrano.
2. After deployment, automatically create snapshot.

You can do rollback.(Using capistrano)

1. Check instances which have specific name.If the instances are stopped, wake them up.
2. Rollback.(capistrano)
3. After rollback, this script will delete latest snapshot.

※Creating/Delete snapshot function is arrangement of [http://heartbeats.jp/hbblog/2011/04/botoebs.html](http://heartbeats.jp/hbblog/2011/04/botoebs.html)

### Requirement

- Make sure that you can deploy application using capistrano, and capistrano-ext. [https://github.com/capistrano/capistrano/wiki](https://github.com/capistrano/capistrano/wiki)
- Python 2.5 < 3.x
- boto package (easy_install boto OR pip install boto)

### Preparation

1. Open ec2helper/config.py.  
Edit access_key, and secret_key in dictionary "AWS_DATA".  
Set key of "REGION" you want to connect to. (If you want to connect to TOKYO region, set "t")  
You can set multiple AWS account.
3. open deploy_example.py.  
Edit「Edit ===」area.

```python
# Account you want to connect.(key of AWS_DATA)
conf.aws_account = 'default'
# Instance name of production environment(p), development enviroment(d). 
conf.instances = {
    'p' : ['production_server1', 'production_server2'],
    'd' : ['dev_server'],
}

# Path of directory exec cap command.
conf.cap_path = '/path/to/cap/directory'

# First argument of cap command.
# Example：if the cap command is "cap production deploy", set "production".
conf.cap_deploy_to = {
    'p' : 'production',
    'd' : 'dev',
}

# Uncomment if you want to create snapshot after deployment.
#conf.create_snapshot = True

# Description of snapshot.Uncoment if you create snapshot.
#conf.snap_description = 'snapshot test'

# If you want to create snapshot in develop enviroment, uncomment this.
#conf.create_snap_only_production = False
```


4. Edit deploy.rb(Capistrano's script).Change "role" to receive host name dynamically.  

```ruby
role :app do
    "#{host}".split(',')
end
```


### How to use

$ python deploy_example.py [enviroment] [deploy command]

Enviroment：  
・p production enviroment
・d develop enviroment

Deploy command:  
・deploy  
・deploy:rollback  
・deploy:cleanup

Example:  
Deploy to dev enviroment.  
$ python deploy_example.py d deploy

Deploy to production enviroment.  
$ python deploy_example.py p deploy

Rollback in dev enviroment.  
$ python deploy_example.py d deploy:rollback

Cleanup in dev enviroment.  
$ python deploy_example.py d deploy:cleanup

You can create snapshot using ec2helper/snapshot.py.  
$ python snapshot.py [snapshot description] -v volume-name(vol-xxxxx)

You can change region using -r option.  
$ python snapshot.py [snapshot description] -v volume-name(vol-xxxxx) -r s  
<small>※Create snapshot of vol-xxxx in singapore region</small>
