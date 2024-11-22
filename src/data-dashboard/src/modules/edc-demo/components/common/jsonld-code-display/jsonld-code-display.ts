import {Component, EventEmitter, Inject, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import { JsonLdObject } from '@think-it-labs/edc-connector-client';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'jsonld-code-display',
  templateUrl: './jsonld-code-display.html',
  styleUrls: ['./jsonld-code-display.scss']
})
export class JsonLdCodeDisplayComponent implements OnChanges {

  @Input() content: JsonLdObject | undefined;
  @Output() contentChange = new EventEmitter<JsonLdObject>();

  @Input() isCopyButton: boolean = false;
  @Input() isEditable: boolean = false;

  jsonString: string = '';

  constructor(
    private snackBar: MatSnackBar,
  ) 
  {
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.content) {
      this.updateJsonString();
    }
  }

  updateJsonString(): void {
    this.jsonString = JSON.stringify(this.content, null, 2);
  }

  onJsonChange(): void {
    try {
      this.content = JSON.parse(this.jsonString);
      console.log(this.content);
      this.contentChange.emit(this.content);
    } catch (e) {
      this.snackBar.open('Incorrect json format', '', {
        duration: 2000,
      });
    }
  }

  public copyToClipboard(): void {
    const jsonString = JSON.stringify(this.content, null, 2);
    navigator.clipboard.writeText(jsonString).then(() => {
      // Show success message when content is copied
      this.snackBar.open('Copied to clipboard!', '', {
        duration: 2000,
      });
    }).catch((err) => {
      console.error('Failed to copy: ', err);
    });
  }
}
