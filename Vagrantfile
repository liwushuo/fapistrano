# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "parallels/ubuntu-14.04"
  config.vm.box_check_update = false
  # config.vm.network "private_network", ip: "192.168.33.10"
  # config.vm.network "public_network"
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.synced_folder "../data", "/vagrant_data"

  config.vm.provider "parallels" do |prl|
    prl.name = "fapistrano"
    prl.check_guest_tools = false
    prl.update_guest_tools = true
    prl.memory = 2048
    prl.cpus = 4
  end

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

end
