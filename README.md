# mydns
## 应用场景

通过配置外网地址和内网地址，将对应外网地址的域名解析到内网ip下

如：

外网ip: `123.23.45.67`

内网ip: `192.168.1.2`

对应域名: `abc.com`

当访问`abc.com`，通过该dns解析后会将域名解析到对应内网ip

## 配置
### `config/mydns_config.yml`

- 确保两个值都有定义
- 添加别的字段不会被读取
- `external_addr` 可以有多个值
- `internal_addr` 只会转发到第一个定义的值
```yaml
external_addr:
    - 0.0.0.0
internal_addr:
    - 1.1.1.1
```

## 使用

### 系统准备

- 优先使用本地dns解析
- 确保本机所有域名都可以正常访问

```bash
systemctl stop systemd-resolved
cat > /etc/resolv.conf << EOF
nameserver 127.0.0.1
nameserver 8.8.8.8
EOF
```

### 构建镜像
也可以直接使用dockerhub上构建好的镜像`mi1ktea/tools:mydns`

```bash
docker build -t mydns:test -f Dockerfile .
```

### 启动容器

```bash
docker run -d --name mydns -v config:/wkdir/config -p 53:53 -p 53:53/udp  mydns:test 
```
