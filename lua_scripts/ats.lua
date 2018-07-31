-- this is executed per thread, each thread has it's copy of 'counter'
counter = 1
math.randomseed( os.time() )
request = function()
   counter = math.random(131072)
   path =  wrk.path .. "testfile_" .. string.format("%012d", counter) .. ".html"
   return wrk.format(nil, path)
end

-- setup each thread with dedicated ip address of host
-- if symbolic name is used, set all aliases in /etc/hosts
-- or use IP address if only single IP is to be tested
local hostcount = 1
local addrs = nil

function setup(thread)
    if not addrs then
        addrs = wrk.lookup(wrk.host, wrk.port or "http")
        for i = #addrs, 1, -1 do
            if not wrk.connect(addrs[i]) then
                table.remove(addrs, i)
            end
        end
    end

    thread.addr = addrs[hostcount]
    hostcount = hostcount + 1
    if hostcount > #addrs then
        hostcount = 1
    end
end

-- for verification purposes print IP address for each thread
function init(args)
    local msg = "thread addr: %s"
    print(msg:format(wrk.thread.addr))
end

-- done() function that prints latency percentiles as CSV
done = function(summary, latency, requests)
    --   io.write("req/s, Mbytes/s, latency.mean, latency.stdev, 50%, 90%, 99%, 99.999% \n")
    local f=io.open("test.log", "a")
    if f ~= nil then
        io.output(f)
        io.write(string.format("%g", (summary.requests*1000000)/summary.duration) )
        io.write(string.format(" ,%g", (summary.bytes/summary.duration )/1.048576))
        io.write(string.format(" ,%d", latency.mean ))
        io.write(string.format(" ,%d", latency.stdev ))

        for _, p in pairs({ 50, 90, 99, 99.999 }) do
            n = latency:percentile(p)
            io.write(string.format(" ,%d", n))
        end
    io.write("\n")
    io.close(f)
end
end

