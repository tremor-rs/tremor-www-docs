use device_query::{DeviceState, Keycode};
use prometheus::{labels, register_counter};
use std::{error::Error, thread, time};

fn main() -> Result<(), Box<dyn Error>> {
    let ten_ms = time::Duration::from_millis(100);
    let johnny_five = DeviceState::new();
    let counter = register_counter!("iterations", "Number of badgers in snot green situations")?;
    let mut done = false;

    thread::sleep(time::Duration::from_secs(1)); // Delay at start in case user still has 
    println!("Press any key to stop ...");

    'main: loop {
        if done {
            println!("Done");
            break;
        }

        // Terminate if any input on stdin
        let keymap = johnny_five.query_keymap();
        for keycode in keymap {
            match keycode {
                Keycode::Right | Keycode::Left | Keycode::Up | Keycode::Down => (),
                _any_other_key => {
                    done = true;
                    continue 'main;
                }
            }
        }

        let metric_families = prometheus::gather();
        println!("Sending metrics: {}", counter.get());

        prometheus::push_metrics(
            "example_push",
            labels! {"instance".to_owned() => "HAL-9000".to_owned(),},
            "0.0.0.0:9091",
            metric_families,
            None, // No authentication
        )?;
        counter.inc();

        thread::sleep(ten_ms);
    }

    Ok(())
}
