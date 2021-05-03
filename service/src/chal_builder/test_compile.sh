#!/usr/bin/env bash
set -x
srcfn=$1
binfn=${srcfn%.tasm}.bin

if [[ $4 != "-run" ]]; then
  docker exec -it cjb2 bash -l -c 'export PATH=$PATH:/opt/sparc/bin:/opt/riscv/bin; source /root/venv/bin/activate; cd /tiamat/service/src/chal_builder; python3 -m compiler '"$srcfn -o $binfn"
  ret=$?

  if [ $ret -ne 0 ]; then
    exit 112
    echo "Compile failed"
  fi
fi
#tmux respawn-pane -t 6:0.1 -k 'cd /cooonj/service/src/chal_builder; printf "aaaabbbbccc\n"| /cooonj/service/qemooo -d op,in_asm,exec,out_asm,cpu junk/exp.bin;zsh'

if [[ $3 == '-debug' ]]; then
  dopts="-d cpu"
else
  dopts="-strace"
fi

tmux_pane_tty="$(tmux list-panes -F '#{pane_tty}'|tail -2|head -1)"
printf "\n-----------------------------------------------------------------\n" > $tmux_pane_tty

printf "$2"| timeout 2s /tiamat/service/qemooo $dopts $binfn > $tmux_pane_tty 2>&1 &

tmux_pane_tty="$(tmux list-panes -F '#{pane_tty}'|tail -1)"
printf "\n-----------------------------------------------------------------\n" > $tmux_pane_tty
printf "$2"| timeout 2s /tiamat/service/qemooo $dopts $binfn > $tmux_pane_tty 2> /dev/null &
#printf "$2"| timeout 2s /cooonj/service/qemooo $dopts $binfn 2> /dev/null |hd  > $tmux_pane_tty  &
